from itertools import product

import numpy as np
import xarray as xr
from tikon.central.errores import ErrorNombreInválido
from tikon.central.simul import PlantillaSimul
from tikon.result.dibs import graficar_res
from tikon.result.valid import ValidÍnds, ValidRes
from tikon.utils import proc_líms, EJE_PARÁMS, EJE_ESTOC, EJE_TIEMPO

from .coso import Coso


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

        símismo._corresp_coords = {}
        for dim in list(coords):
            if any(isinstance(x, Coso) for x in coords[dim]):
                símismo._corresp_coords[dim] = coords[dim]

        símismo.datos_t = _gen_datos(símismo.nombre, coords, t=símismo.t)
        símismo.datos_t.attrs['unids'] = símismo.unids

        # Crear enlace dinámico entre resultados diarios y temporales
        símismo._datos = símismo.datos_t[{EJE_TIEMPO: 0}].drop_vars(EJE_TIEMPO)

        símismo._textificar_ejes()
        símismo.coords = {ll: list(v.values) for ll, v in símismo._datos.coords.items()}

        super().__init__(símismo.nombre, subs=[])

    @property
    def datos(símismo):
        return símismo._datos

    def poner_valor(símismo, val, rel=False):
        if isinstance(val, xr.DataArray):
            coords = {
                ll: v for ll, v in val.indexes.items()
                if v.shape != símismo._datos.indexes[ll].shape or np.any(v != símismo._datos.indexes[ll])
            }
            if coords:
                val = val.broadcast_like(símismo._datos.loc[coords])
                if rel:
                    símismo._datos.loc[coords] += val
                else:
                    símismo._datos.loc[coords] = val
            else:
                val = val.broadcast_like(símismo._datos)
                if rel:
                    símismo._datos.variable[:] += val  # Más rápido que _datos o _datos[:]
                else:
                    símismo._datos.variable[:] = val  # Más rápido que  _datos[:]
        else:
            if rel:
                símismo._datos.values += val
            else:
                símismo._datos.values[:] = val

    def poner_valor_matr(símismo, matr, eje, índs, rel=False):
        rbnd = símismo._rebanar(eje, índs=índs)

        if isinstance(matr, np.ndarray):
            forma = tuple([*matr.shape, *[1] * (len(símismo.datos.values.shape) - len(matr.shape))])
            val = matr.reshape(forma)
        else:
            val = matr
        if rel:
            símismo.datos.values[rbnd] += val
        else:
            símismo.datos.values[rbnd] = val

    def iniciar(símismo):
        símismo._textificar_ejes()

        símismo.datos_t.values[:] = 0
        símismo._datos = símismo.datos_t[{EJE_TIEMPO: 0}].drop_vars(EJE_TIEMPO)

        if símismo.inicializable:
            inic = símismo.sim.simul_exper.paráms_exper[str(símismo.sim)][str(símismo)]
            símismo.poner_valor(inic.matr.val)

    def incrementar(símismo, paso, f):
        if símismo.t is not None:
            símismo._datos = símismo.datos_t[{EJE_TIEMPO: símismo.t.i}].drop_vars(EJE_TIEMPO)
            símismo._datos.values[:] = símismo.datos_t[{EJE_TIEMPO: símismo.t.i - 1}].values

    def cerrar(símismo):
        for dim, crds in símismo._corresp_coords.items():
            símismo._datos[dim] = crds
            símismo.datos_t[dim] = crds

    def verificar_estado(símismo):
        if np.any(~np.isfinite(símismo.datos)):
            raise ValueError('{res}: Valor no numérico (p. ej., división por 0)'.format(res=símismo))

        if símismo.líms:
            mín, máx = proc_líms(símismo.líms)

            if np.any(símismo.datos < mín) or np.any(símismo.datos > máx):
                raise ValueError(
                    '{res}: Valor de afuera de los límites {líms}'.format(res=símismo, líms=repr(símismo.líms))
                )

    def validar(símismo, proc):
        l_proc = []
        for obs in símismo.obs:
            resultados = obs.proc_res(símismo.datos_t)
            res_corresp = resultados.interp_like(obs.datos).dropna(EJE_TIEMPO)
            obs_corresp = obs.datos.loc[{EJE_TIEMPO: res_corresp[EJE_TIEMPO]}]

            for índs in símismo.iter_índs(obs.datos, excluir=EJE_TIEMPO):
                datos_índs = res_corresp.loc[índs]
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
            resultados = obs.proc_res(símismo.datos_t)
            res_corresp = resultados.interp_like(obs.datos[EJE_TIEMPO]).dropna(EJE_TIEMPO)
            obs_corresp = obs.datos.loc[{EJE_TIEMPO: res_corresp[EJE_TIEMPO]}]

            for índs in símismo.iter_índs(obs.datos, excluir=EJE_TIEMPO):
                obs_índs = obs_corresp.loc[índs]

                l_proc.append(proc.calc(obs_índs, res_corresp.loc[índs]))
                pesos.append(proc.pesos(obs_índs))
        if l_proc:
            return proc.combin(np.array(l_proc), pesos=pesos), proc.combin_pesos(pesos)
        return 0, 0

    def graficar(símismo, directorio='', argsll=None):
        if símismo.t is not None:
            argsll = argsll or {}
            for índs in símismo.iter_índs(símismo.datos_t, excluir=[EJE_TIEMPO, EJE_ESTOC, EJE_PARÁMS]):
                título = ', '.join(ll + ' ' + str(v) for ll, v in índs.items())

                obs_índs = []
                for o_ in símismo.obs:
                    try:
                        obs_índs.append(o_.datos.loc[índs])
                    except KeyError:
                        pass

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

    def _textificar_ejes(símismo):
        for dim, crds in símismo._corresp_coords.items():
            símismo._datos[dim] = [str(x) for x in símismo._datos.coords[dim].values]
            símismo.datos_t[dim] = [str(x) for x in símismo.datos_t.coords[dim].values]

    def _rebanar(símismo, eje, índs):
        índs = [símismo.coords[eje].index(í) for í in índs]
        return tuple([slice(None)] * símismo.datos.dims.index(eje) + [índs])

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
