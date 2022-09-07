from itertools import product

import numpy as np
import xarray as xr
from frozendict import frozendict

from tikon.central.errores import ErrorNombreInválido
from tikon.central.simul import PlantillaSimul
from tikon.datos.datos import Datos
from tikon.datos.dibs import graficar_res
from tikon.datos.valid import ValidÍnds, ValidRes
from tikon.ecs.aprioris import APrioriDens
from tikon.utils import proc_líms, EJE_PARÁMS, EJE_ESTOC, EJE_TIEMPO, guardar_json, asegurar_dir_existe, asegurar_ext


class Resultado(PlantillaSimul):
    líms = None
    inicializable = False
    apriori = None

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

        símismo._datos_t = _gen_datos(símismo.nombre, coords, t=símismo.t)
        símismo._datos_t.atribs['unids'] = símismo.unids

        # Crear enlace dinámico entre resultados diarios y temporales
        símismo._datos = símismo._datos_t[{EJE_TIEMPO: 0}]
        símismo.activada = símismo._datos.matr.size != 0
        símismo.res = None

        super().__init__(símismo.nombre, subs=[])

    @property
    def datos(símismo):
        return símismo._datos

    def apriori_de_obs(símismo, obs, índ):
        datos_obs = [o_.datos.loc[índ] for o_ in obs if índ in o_]
        líms = proc_líms(símismo.líms)
        if datos_obs:
            mín, máx = np.nanmin([o_.min() for o_ in datos_obs]), np.nanmax([o_.max() for o_ in datos_obs])
            mín = max(mín, líms[0])
            máx = min(máx, líms[1])
            return APrioriDens((mín, máx), 0.5)

    def poner_valor(símismo, val, rel=False):
        if isinstance(val, Datos):
            if rel:
                símismo._datos.loc[val] += val
            else:
                símismo._datos.loc[val] = val
        else:
            if rel:
                símismo._datos += val
            else:
                símismo._datos[:] = val

    def iniciar(símismo):
        if not símismo.activada:
            return
        símismo._datos_t[:] = 0
        símismo._datos = símismo._datos_t[{EJE_TIEMPO: 0}]

        if símismo.inicializable:
            inic = símismo.sim.simul_exper.paráms_exper[str(símismo.sim)][str(símismo)]
            símismo.poner_valor(inic.matr.val)

    def avanzar_datos(símismo):
        if símismo.activada and símismo.t is not None:
            símismo._datos = símismo._datos_t[{EJE_TIEMPO: símismo.t.i}]
            símismo._datos[:] = símismo._datos_t[{EJE_TIEMPO: símismo.t.i - 1}]

    def cerrar(símismo):
        símismo.res = símismo._datos_t.a_xarray()

    def verificar_estado(símismo):
        if not símismo.activada:
            return
        if np.any(~np.isfinite(símismo.datos.matr)):
            raise ValueError('{res}: Valor no numérico (p. ej., división por 0)'.format(res=símismo))

        if símismo.líms:
            mín, máx = proc_líms(símismo.líms)

            if np.any(símismo.datos.matr < mín) or np.any(símismo.datos.matr > máx):
                raise ValueError(
                    '{res}: Valor fuera de los límites {líms}'.format(res=símismo, líms=repr(símismo.líms))
                )

    def validar(símismo, proc):
        l_proc = []
        for obs in símismo.obs:
            resultados = obs.proc_res(símismo.res)
            res_corresp = resultados.interp_like(obs.datos).dropna(EJE_TIEMPO, how='all')
            obs_corresp = obs.datos.loc[{EJE_TIEMPO: res_corresp[EJE_TIEMPO]}]

            for índs in símismo.iter_índs(obs.datos, excluir=EJE_TIEMPO):
                datos_índs = res_corresp.loc[índs]
                obs_índs = obs_corresp.loc[índs]
                l_proc.append(
                    ValidÍnds(
                        criterios=proc.calc(obs_índs, datos_índs), peso=proc.pesos(obs_índs), índs=índs
                    )
                )

        return ValidRes(l_proc, proc=proc)

    def procesar_calib(símismo, proc):
        l_proc = []
        pesos = []
        for obs in símismo.obs:
            resultados = obs.proc_res(símismo.res)
            res_corresp = resultados.interp_like(obs.datos[EJE_TIEMPO]).dropna(EJE_TIEMPO, how='all')
            obs_corresp = obs.datos.loc[{EJE_TIEMPO: res_corresp[EJE_TIEMPO]}]

            for índs in símismo.iter_índs(obs.datos, excluir=EJE_TIEMPO):
                obs_índs = obs_corresp.loc[índs]
                ejes_combin = [ll for ll in índs if isinstance(índs[ll], tuple)]
                res_índs = res_corresp.loc[
                    {ll: list(v) if ll in ejes_combin else v for ll, v in índs.items()}
                ].sum(ejes_combin)
                l_proc.append(proc.calc(obs_índs, res_índs))
                pesos.append(proc.pesos(obs_índs))
        if l_proc:
            return proc.combin(np.array(l_proc), pesos=pesos), proc.combin_pesos(pesos)
        return 0, 0

    def graficar(símismo, directorio='', argsll=None):
        if símismo.t is not None:
            argsll = argsll or {}
            for índs in símismo.iter_índs(símismo.res, excluir=[EJE_TIEMPO, EJE_ESTOC, EJE_PARÁMS]):
                título = ', '.join(ll + ' ' + str(v) for ll, v in índs.items())

                obs_índs = []
                for o_ in símismo.obs:
                    try:
                        obs_índs.append(o_.datos.loc[índs])
                    except KeyError:
                        pass

                graficar_res(
                    título, directorio,
                    simulado=símismo.res.loc[índs], obs=obs_índs, **argsll
                )

    def a_dic(símismo):
        if símismo.t is not None:
            return {
                'obs': símismo.obs.a_dic() if símismo.obs else None,
                'preds': símismo.res.a_xarray().to_dict(),
            }

    def guardar(símismo, archivo, formato='netcdf'):

        res = símismo.res.copy()
        for dim, crds in res.coords.items():
            res.coords[dim] = [
                str(x) if not (np.issubdtype(crds.dtype, np.int) or np.issubdtype(crds.dtype, np.datetime64))
                else x for x in crds.values
            ]

        formato = formato.lower().strip('.')
        if formato == 'netcdf':
            archivo = asegurar_ext(archivo, '.nc')
            asegurar_dir_existe(archivo)
            res.to_netcdf(archivo, mode='w')
        elif formato == 'json':
            archivo = asegurar_ext(archivo, '.json')
            guardar_json(res.to_dict(), archivo=archivo)
        else:
            raise ValueError(formato)

    @staticmethod
    def iter_índs(datos, excluir=None):
        if isinstance(datos, xr.DataArray):
            datos = Datos.de_xarray(datos)
        excluir = excluir or []
        if isinstance(excluir, str):
            excluir = [excluir]

        dims = [dim for dim in datos.dims if dim not in excluir]
        for índs in product(*[datos.coords[dim] for dim in dims]):
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
    return Datos(0., dims=list(coords), coords=coords, nombre=nombre)
