from itertools import product

import numpy as np
import xarray as xr
from tikon.central.errores import ErrorNombreInválido
from tikon.central.simul import PlantillaSimul
from tikon.result.dibs import graficar_res
from tikon.result.valid import ValidÍnds, ValidRes
from tikon.utils import proc_líms, EJE_PARÁMS, EJE_ESTOC, EJE_TIEMPO


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

        símismo.datos_t = _gen_datos(símismo.nombre, coords, t=símismo.t)
        símismo.datos_t.attrs['unids'] = símismo.unids
        símismo._datos = símismo.datos_t[{EJE_TIEMPO: 0}]  # Crear enlace dinámico entre resultados diarios y temporales

        super().__init__(símismo.nombre, subs=[])

    @property
    def datos(símismo):
        return símismo._datos.drop_vars(EJE_TIEMPO)

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
            inic = símismo.sim.simul_exper.paráms_exper[str(símismo.sim)][str(símismo)]
            if inic is not None:
                símismo.datos = inic.matr.val

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
        l_proc = []
        for obs in símismo.obs:
            datos_corresp = símismo.datos_t.interp_like(obs.datos).dropna(EJE_TIEMPO)
            obs_corresp = obs.datos.loc[{EJE_TIEMPO: datos_corresp[EJE_TIEMPO]}]

            for índs in símismo.iter_índs(obs.datos, excluir=EJE_TIEMPO):
                datos_índs = obs.proc_res(datos_corresp.loc[índs])
                obs_índs = obs_corresp.loc[índs]
                l_proc.append(
                    ValidÍnds(
                        criterios=proc.calc(obs_índs, datos_índs), peso=proc.pesos(obs_índs)
                    )
                )

        return ValidRes(l_proc, proc=proc)

    def procesar_calib(símismo, proc):
        l_proc = []
        pesos = []
        for obs in símismo.obs:
            datos_corresp = símismo.datos_t.interp_like(obs.datos).dropna(EJE_TIEMPO)
            obs_corresp = obs.datos.loc[{EJE_TIEMPO: datos_corresp[EJE_TIEMPO]}]

            for índs in símismo.iter_índs(obs.datos, excluir=EJE_TIEMPO):
                obs_índs = obs_corresp.loc[índs]

                l_proc.append(proc.calc(obs_índs, datos_corresp.loc[índs]))
                pesos.append(proc.pesos(obs_índs))

            return proc.combin(l_proc, pesos=pesos), proc.combin_pesos(pesos)

        return 0, 0

    def graficar(símismo, directorio='', argsll=None):
        if símismo.t is not None:
            argsll = argsll or {}
            for índs in símismo.iter_índs(símismo.datos_t, excluir=[EJE_TIEMPO, EJE_ESTOC, EJE_PARÁMS]):
                título = ', '.join(ll + ' ' + str(v) for ll, v in índs.items())

                obs_índs = [o_.datos.loc[índs] for o_ in símismo.obs]
                graficar_res(
                    título, directorio,
                    simulado=símismo.datos_t.loc[índs], obs=obs_índs, **argsll
                )

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
        return len(obs) > 0

    return nombre_sim in vars_interés or nombre_sim + '.' + nombre in vars_interés


def _gen_datos(nombre, coords, t):
    coords = {EJE_TIEMPO: t.eje if t is not None else [0], **coords}
    return xr.DataArray(data=0., coords=coords, dims=list(coords), name=nombre)
