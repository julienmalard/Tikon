import numpy as np
import spotpy.objectivefunctions as of
from spotpy.likelihoods import gaussianLikelihoodMeasErrorOut
from tikon.result import EJE_ESTOC, EJE_PARÁMS


# Funciones pesos
def n_existen(x):
    return np.isfinite(x).sum(dim='tiempo').values.item()


# Funciones vals
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


# Funciones combin vals
def prom_vals(vals, pesos):
    return np.average(vals, weights=pesos)


# Funciones combin pesos
def suma_pesos(pesos):
    return np.sum(pesos)


class Procesador(object):
    def __init__(símismo, f_vals=ens, f_pesos=n_existen, f_combin=prom_vals, f_combin_pesos=suma_pesos):
        símismo.f_vals = f_vals
        símismo.f_pesos = f_pesos
        símismo.f_combin = f_combin
        símismo.f_combin_pesos = f_combin_pesos


class ProcesadorValids(Procesador):
    def __init__(símismo, f_vals=ens, f_pesos=n_existen, f_combin=prom_vals, f_combin_pesos=suma_pesos):
        if callable(f_vals):
            f_vals = [f_vals]
        if isinstance(f_vals, list):
            f_vals = {f.__name__: f for f in f_vals}

        def f_final_vals(o, s):
            return {ll: v(o, s) for ll, v in f_vals.items()}

        def f_final_combin()

        super().__init__(f_final_vals, f_pesos, f_combin, f_combin_pesos)
