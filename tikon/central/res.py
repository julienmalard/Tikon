from itertools import product

import numpy as np
import xarray as xr
from tikon.central.errores import ErrorNombreInválido
from tikon.central.simul import PlantillaSimul
from tikon.central.utils import EJE_TIEMPO, EJE_PARÁMS, EJE_ESTOC
from tikon.result.dibs import graficar_res
from tikon.result.valid import reps_necesarias
from tikon.utils import proc_líms


class Resultado(PlantillaSimul):
    líms = None
    inicializable = False

    def __init__(símismo, sim, coords, vars_interés):
        if '.' in símismo.nombre:
            raise ErrorNombreInválido(
                'Nombre {nombre} inválido: Nombres de resultados no pueden contener ".".'.format(nombre=símismo.nombre)
            )

        símismo.sim = sim
        símismo.obs = sim.exper.datos.obt_obs(sim, símismo)

        símismo.t = sim.simul_exper.t if _res_temporal(
            símismo.nombre, sim.mód.nombre, símismo.obs, vars_interés
        ) else None

        símismo.datos_t = _gen_datos(coords, t=símismo.t)
        símismo._datos = símismo.datos_t[{EJE_TIEMPO: 0}]  # Crear enlace dinámico entre resultados diarios y temporales

        super().__init__(símismo.nombre, subs=[])

    @property
    def datos(símismo):
        return símismo._datos.drop(EJE_TIEMPO)

    @datos.setter
    def datos(símismo, val):
        if isinstance(val, xr.DataArray):
            símismo._datos.loc[val.coords] = val.broadcast_like(símismo._datos.loc[val.coords])
        else:
            símismo._datos[:] = val

    def iniciar(símismo):
        símismo.datos_t[:] = 0
        símismo._datos = símismo.datos_t[{EJE_TIEMPO: 0}]

        if símismo.inicializable:
            for índs in símismo.iter_índs(símismo.datos, excluir=[EJE_TIEMPO, EJE_PARÁMS, EJE_ESTOC]):
                inic = símismo.sim.exper.datos.obt_inic(mód=símismo.sim, var=símismo, índs=índs)
                if inic:
                    símismo._datos.loc[índs] = inic

    def incrementar(símismo, paso, f):
        if símismo.t is not None:
            símismo._datos = símismo.datos_t[{EJE_TIEMPO: símismo.t.i}]
            símismo._datos[:] = símismo.datos_t[{EJE_TIEMPO: símismo.t.i - 1}]

    def cerrar(símismo):
        pass

    def verificar_estado(símismo):
        if símismo.líms:
            mín, máx = proc_líms(símismo.líms)

            if np.any(símismo.datos < mín) or np.any(símismo.datos > máx):
                raise ValueError(
                    '{res}: Valor de afuera de los límites {líms}'.format(res=símismo, líms=repr(símismo.líms))
                )
            if np.any(np.isnan(símismo.datos)):
                raise ValueError('{res}: Valor no numérico (p. ej., división por 0)'.format(res=símismo))

    def validar(símismo, proc):
        if símismo.obs is not None:
            obs_corresp = símismo.obs.interp_like(símismo.datos_t)

            l_proc = []
            pesos = []
            d_valid = {}
            for índs in símismo.iter_índs(símismo.obs, excluir=EJE_TIEMPO):

                l_llaves = list(str(ll) for ll in índs.values())

                dic = d_valid
                for ll in l_llaves[:-1]:
                    if ll not in dic:
                        dic[ll] = {}
                    dic = dic[ll]

                dic[l_llaves[-1]] = proc.f_vals(símismo.datos_t.loc[índs], obs_corresp.loc[índs])

            return d_valid

    def procesar_calib(símismo, proc):

        if símismo.obs is not None:
            obs_corresp = símismo.obs.interp_like(símismo.datos_t)

            l_proc = []
            pesos = []
            for índs in símismo.iter_índs(símismo.obs, excluir=EJE_TIEMPO):
                obs_índs = obs_corresp.loc[índs]

                l_proc.append(proc.f_vals(obs_índs, símismo.datos_t.loc[índs]))
                pesos.append(proc.f_pesos(obs_índs))

            return proc.f_vals(l_proc, pesos=pesos), proc.f_pesos(pesos)

        return 0, 0

    def graficar(símismo, directorio='', argsll=None):
        if símismo.datos_t.t is not None:
            argsll = argsll or {}
            for índs in símismo.iter_índs(símismo.datos_t, excluir=[EJE_TIEMPO, EJE_ESTOC, EJE_PARÁMS]):
                título = ', '.join(ll + ' ' + str(v) for ll, v in índs.items())

                obs_índs = símismo.obs.loc[índs] if símismo.obs is not None else None
                graficar_res(
                    título, directorio,
                    simulado=símismo.datos_t.loc[índs], obs=obs_índs, **argsll
                )

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        return reps_necesarias(símismo.datos_t, frac_incert=frac_incert, confianza=confianza)

    def a_dic(símismo):
        if símismo.t is not None:
            return {
                'obs': símismo.obs.a_dic() if símismo.obs else None,
                'preds': símismo.datos_t.to_dict(),
            }

    @staticmethod
    def iter_índs(datos, excluir=None):
        excluir = excluir or []
        if isinstance(excluir, str):
            excluir = [excluir]

        dims = [dim for dim in datos.dims if dim not in excluir]
        for índs in product(*[datos[dim].values for dim in dims]):
            yield dict(zip(dims, índs))

    @property
    def nombre(símismo):
        raise NotImplementedError

    @property
    def unids(símismo):
        raise NotImplementedError

    def __str__(símismo):
        return símismo.nombre


def _res_temporal(nombre, nombre_sim, obs, vars_interés):
    if isinstance(vars_interés, bool):
        return vars_interés

    if vars_interés is None:
        return obs is not None

    return nombre_sim in vars_interés or nombre_sim + '.' + nombre in vars_interés


def _gen_datos(coords, t):
    coords = {EJE_TIEMPO: t.eje if t is not None else [0], **coords}
    return xr.DataArray(data=0., coords=coords, dims=list(coords))


class Resultado0(object):
    def __init__(símismo, nombre, dims, tiempo=None, obs=None, inic=None):

        símismo.obs = obs
        símismo.inic = inic

    def reinic(símismo):
        super().reinic()

        if símismo.obs:
            t_inic = símismo.tiempo.día()  # para hacer: con f_inic

            dims_obs = símismo.obs.dims

            # para hacer: en una única llamada a poner_valor() en cuanto funcionen los índices múltiples en rebanar()
            for índs in dims_obs.iter_índs(excluir=EJE_TIEMPO):
                vals_inic = símismo.obs.obt_val_t(t_inic, índs=índs)

                vals_inic[np.isnan(vals_inic)] = 0
                símismo.poner_valor(vals=vals_inic, índs=índs)

            símismo.actualizar()

        if símismo.inic:
            for val in símismo.inic:
                símismo.poner_valor(vals=val.valor(), índs=val.índs)
            símismo.actualizar()
