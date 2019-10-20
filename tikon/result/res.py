import numpy as np
import xarray as xr
from spotpy.likelihoods import gaussianLikelihoodMeasErrorOut
from spotpy.objectivefunctions import nashsutcliffe, rmse, agreementindex, kge, rrmse, rsquared, log_p
from tikon.estruc.simul import PlantillaSimul
from tikon.result.dibujar import graficar_pred
from tikon.result.valid import reps_necesarias, validar_matr_pred
from tikon.utils import TIEMPO


class Resultado(PlantillaSimul):
    def __init__(símismo, nombre, coords, t=None, obs=None):
        símismo.datos_t = _gen_datos(coords, t=t)
        símismo._datos = símismo.datos_t[{TIEMPO: 0}]

        super().__init__(nombre, subsimuls=[])

    @property
    def datos(símismo):
        return símismo._datos

    @datos.setter
    def datos(símismo, val):
        símismo._datos[:] = val

    def iniciar_estruc(símismo):
        pass

    def iniciar_vals(símismo):
        símismo.datos_t[:] = 0
        símismo.datos = símismo.datos_t[{TIEMPO: 0}]

    def incrementar(símismo, paso):
        if símismo.t is not None:
            símismo.datos = símismo.datos_t[{TIEMPO: símismo.t.i}]
        super().incrementar(paso)

    def cerrar(símismo):
        pass

    def verificar_estado(símismo):
        pass

    # para hacer: reorganizar las 4 funciones siguientes
    def validar(símismo):
        if símismo._validable():
            d_valid = {}
            eje_tiempo = símismo.obs.eje_tiempo.cortar(símismo.tiempo.eje)
            for índs in símismo.obs.iter_índs(excluir='días'):
                matr_t = símismo.matr_t
                ejes_orig = np.argsort([matr_t.í_eje('días'), matr_t.í_eje('estoc'), matr_t.í_eje('parám')])

                vals_res = símismo.obt_valor_t(eje_tiempo, índs=índs)
                vals_res = np.moveaxis(vals_res, ejes_orig, [0, 1, 2])
                vals_res = vals_res.reshape(vals_res.shape[:3])
                vals_obs = símismo.obs.obt_valor({**índs, 'días': eje_tiempo.días})

                dic = d_valid
                l_llaves = list(str(ll) for ll in índs.values())
                for ll in l_llaves[:-1]:
                    if ll not in dic:
                        dic[ll] = {}
                        dic = dic[ll]
                dic[l_llaves[-1]] = validar_matr_pred(vals_res, vals_obs)
            return d_valid

    def procesar_calib(símismo, proc):
        if símismo._validable():
            f = f or 'ens'
            if isinstance(f, str):
                f = _funcs[f]
            l_proc = []
            pesos = []
            eje_tiempo = símismo.obs.eje_tiempo.cortar(símismo.tiempo.eje)
            for índs in símismo.obs.iter_índs(excluir='días'):
                matr_t = símismo.matr_t
                ejes_orig = np.argsort([matr_t.í_eje('días'), matr_t.í_eje('estoc'), matr_t.í_eje('parám')])

                vals_res = símismo.obt_valor_t(eje_tiempo, índs=índs)
                vals_res = np.moveaxis(vals_res, ejes_orig, [0, 1, 2])
                vals_res = vals_res.reshape(vals_res.shape[:3])
                vals_obs = símismo.obs.obt_valor({**índs, 'días': eje_tiempo.días})

                # l_proc.append(dens_con_pred(vals_obs, vals_res))

                # para hacer: formalizar opciones de algoritmo especificados por el usuario
                l_proc.append(f(vals_obs, vals_res))
                pesos.append(np.sum(np.isfinite(vals_obs)))
            return np.average(l_proc, weights=pesos), np.sum(pesos)
        return 0, 0

    def graficar(símismo, directorio=''):
        if símismo.matr_t:
            matr_t = símismo.matr_t
            for índs in matr_t.iter_índs(excluir=['días', 'estoc', 'parám']):
                ord_ejes = np.argsort([matr_t.í_eje('días'), matr_t.í_eje('estoc'), matr_t.í_eje('parám')])

                vals_res = símismo.obt_valor_t(símismo.tiempo.eje.vec(), índs=índs)
                vals_res = np.moveaxis(vals_res, ord_ejes, [0, 1, 2])
                try:
                    eje_obs = símismo.obs.eje_tiempo.cortar(símismo.tiempo.eje).vec()
                    vals_obs = símismo.obs.obt_valor({**índs, 'días': eje_obs})
                except (ValueError, AttributeError):  # para hacer: más elegante
                    vals_obs = eje_obs = None

                título = ', '.join(ll + ' ' + str(v) for ll, v in índs.items())

                graficar_pred(
                    título, directorio,
                    vals_res, t_pred=símismo.tiempo.eje.vec(), t_obs=eje_obs, vector_obs=vals_obs,
                )

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        matr = símismo.matr_t or símismo
        return reps_necesarias(
            matr.obt_valor(), eje_parám=matr.í_eje('parám'), eje_estoc=matr.í_eje('estoc'),
            frac_incert=frac_incert, confianza=confianza
        )

    def a_dic(símismo):
        return símismo.datos_t.to_dict()


def _gen_datos(coords, t=None):
    coords = {TIEMPO: t.eje() if t is not None else [0], **coords}
    return xr.DataArray(data=0, coords=coords, dims=list(coords))


class Resultado0(Matriz):
    def __init__(símismo, nombre, dims, tiempo=None, obs=None, inic=None):
        super().__init__(dims)
        símismo.nombre = nombre

        if tiempo:
            símismo.matr_t = MatrizTiempo(dims, tiempo.eje)
        else:
            símismo.matr_t = None

        símismo.obs = obs
        símismo.inic = inic

    def reinic(símismo):
        super().reinic()

        if símismo.obs:
            t_inic = símismo.tiempo.día()  # para hacer: con f_inic

            dims_obs = símismo.obs.dims

            # para hacer: en una única llamada a poner_valor() en cuanto funcionen los índices múltiples en rebanar()
            for índs in dims_obs.iter_índs(excluir='días'):
                vals_inic = símismo.obs.obt_val_t(t_inic, índs=índs)

                vals_inic[np.isnan(vals_inic)] = 0
                símismo.poner_valor(vals=vals_inic, índs=índs)

            símismo.actualizar()

        if símismo.inic:
            for val in símismo.inic:
                símismo.poner_valor(vals=val.valor(), índs=val.índs)
            símismo.actualizar()

    def a_dic(símismo):
        if símismo.matr_t is not None:
            return {
                'obs': símismo.obs.a_dic() if símismo.obs else None,
                'preds': símismo.matr_t.a_dic(),
            }

    def _validable(símismo):
        return símismo.matr_t is not None and símismo.obs is not None


def _ens_dens(o, s):
    prom_obs = np.nanmean(o)
    num = np.nansum((o - s) ** 2, axis=0)
    denom = np.nansum((o - prom_obs) ** 2, axis=0)
    return np.mean(1 - (num / denom))


_funcs = {
    'ens': lambda o, s: nashsutcliffe(o, np.mean(s, axis=(1, 2))),
    'rcep': lambda o, s: -rmse(o, np.mean(s, axis=(1, 2))),
    'corresp': lambda o, s: agreementindex(o, np.mean(s, axis=(1, 2))),
    'ekg': lambda o, s: kge(o, np.mean(s, axis=(1, 2))),
    'r2': lambda o, s: rsquared(o, np.mean(s, axis=(1, 2))),
    'rcnep': lambda o, s: -rrmse(o, np.mean(s, axis=(1, 2))),
    'log p': lambda o, s: log_p(o, np.mean(s, axis=(1, 2))),
    'dens': _ens_dens,
    'verosimil_gaus': gaussianLikelihoodMeasErrorOut
}


class CombinadorEval(object):
    def __init__(símismo, ):
        pass
