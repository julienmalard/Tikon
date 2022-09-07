import numpy as np
import spotpy.objectivefunctions as of
import xarray as xr

from spotpy.likelihoods import gaussianLikelihoodMeasErrorOut

# Funciones pesos
from tikon.utils import EJE_PARÁMS, EJE_ESTOC, EJE_TIEMPO


def n_existen(x):
    return np.isfinite(x).sum(dim=EJE_TIEMPO).values.item()


# Funciones criterios
def ens(o: xr.DataArray, s: xr.DataArray) -> float:
    ev = of.nashsutcliffe(o.values, s.median(dim=(EJE_PARÁMS, EJE_ESTOC)).values)
    if np.isnan(ev):
        return 1
    elif np.isinf(ev):
        return -1e100
    return ev


def rcep(o: xr.DataArray, s: xr.DataArray) -> float:
    return -of.rmse(o.values, s.median(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def corresp(o: xr.DataArray, s: xr.DataArray) -> float:
    return of.agreementindex(o.values, s.median(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def ekg(o: xr.DataArray, s: xr.DataArray) -> float:
    return of.kge(o.values, s.median(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def r2(o: xr.DataArray, s: xr.DataArray) -> float:
    return of.rsquared(o.values, s.median(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def rcnep(o: xr.DataArray, s: xr.DataArray) -> float:
    return -of.rrmse(o.values, s.median(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def log_p(o: xr.DataArray, s: xr.DataArray) -> float:
    return of.log_p(o.values, s.median(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def verosimil_gaus(o: xr.DataArray, s: xr.DataArray) -> float:
    return gaussianLikelihoodMeasErrorOut(o.values, s.median(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


# Funciones criterios con incertidumbre:
def distancia_del_centro(o: xr.DataArray, s: xr.DataArray) -> float:
    distancia = np.abs(o - s.median(dim=(EJE_PARÁMS, EJE_ESTOC)))
    desv = np.maximum(1, s.std(dim=(EJE_PARÁMS, EJE_ESTOC)))
    return (- distancia / desv).values.mean()


def cuantiles(o: xr.DataArray, s: xr.DataArray) -> float:
    cuantil = (o < s).mean(dim=(EJE_PARÁMS, EJE_ESTOC))
    ajustado = 0.5 - np.abs(0.5 - cuantil)
    desv_típica = np.maximum(s.std(dim=(EJE_PARÁMS, EJE_ESTOC)), 1)
    return np.where(
        cuantil == 1,
        -(s.min(dim=(EJE_PARÁMS, EJE_ESTOC)) - o)/desv_típica,
        np.where(
            cuantil == 0,
            -(o - s.max(dim=(EJE_PARÁMS, EJE_ESTOC)))/desv_típica,
            ajustado
        )
    ).min()


# Funciones criterios incertidumbre
def r2_percentiles(o: xr.DataArray, s: xr.DataArray):
    conf = _calc_conf(o, s)
    return of.rsquared(conf, _calc_cent(o))


def rcnep_percentiles(o: xr.DataArray, s: xr.DataArray):
    conf = _calc_conf(o, s)
    return of.rrmse(conf, _calc_cent(o))


def _calc_cent(o):
    return np.arange(1, len(o) + 1) / len(o)


def _calc_conf(o: xr.DataArray, s: xr.DataArray):
    perc = (s <= o).mean(dim=[EJE_ESTOC, EJE_PARÁMS]).values
    conf = np.abs(0.5 - perc) * 2
    conf.sort()
    return conf


# Funciones combin vals
def prom_vals(vals, pesos):
    if not len(vals):
        return None
    pesos = np.array(pesos)
    if np.sum(pesos) == 0:
        pesos[:] = 1
    return np.average(vals, weights=pesos)


# Funciones combin pesos
def suma_pesos(pesos):
    return np.sum(pesos)


class Procesador(object):
    def __init__(símismo, f_vals=ens, f_pesos=n_existen, f_combin=prom_vals, f_combin_pesos=suma_pesos):
        símismo.calc = f_vals
        símismo.pesos = f_pesos
        símismo.combin = f_combin
        símismo.combin_pesos = f_combin_pesos


def gen_proc(proc):
    if isinstance(proc, Procesador):
        return proc
    return Procesador(f_vals=proc)
