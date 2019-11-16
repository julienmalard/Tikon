import numpy as np
import spotpy.objectivefunctions as of
from spotpy.likelihoods import gaussianLikelihoodMeasErrorOut

# Funciones pesos
from tikon.utils import EJE_PARÁMS, EJE_ESTOC


def n_existen(x):
    return np.isfinite(x).sum(dim='tiempo').values.item()


# Funciones criterios
def ens(o, s):
    return of.nashsutcliffe(o.values, s.mean(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def rcep(o, s):
    return -of.rmse(o.values, s.mean(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def corresp(o, s):
    return of.agreementindex(o.values, s.mean(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def ekg(o, s):
    return of.kge(o.values, s.mean(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def r2(o, s):
    return of.rsquared(o.values, s.mean(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def rcnep(o, s):
    return -of.rrmse(o.values, s.mean(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def log_p(o, s):
    return of.log_p(o.values, s.mean(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


def verosimil_gaus(o, s):
    return gaussianLikelihoodMeasErrorOut(o.values, s.mean(dim=(EJE_PARÁMS, EJE_ESTOC)).values)


# Funciones criterios incertidumbre
def r2_percentiles(o, s):
    conf = _calc_conf(o, s)
    return of.rsquared(conf, _calc_cent(o))


def rcnep_percentiles(o, s):
    conf = _calc_conf(o, s)
    return of.rrmse(conf, _calc_cent(o))


def _calc_cent(o):
    return np.arange(1, len(o) + 1) / len(o)


def _calc_conf(o, s):
    perc = (s <= o).mean(dim=[EJE_ESTOC, EJE_PARÁMS]).values
    conf = np.abs(0.5 - perc) * 2
    conf.sort()
    return conf


# Funciones combin vals
def prom_vals(vals, pesos):
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
