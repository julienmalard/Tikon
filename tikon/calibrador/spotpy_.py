import math as mat
import tempfile

import numpy as np
import pandas as pd
import spotpy as spt
from tikon.calibrador.calib import Calibrador


class CalibSpotPy(Calibrador):
    dists_disp = ['Normal', 'Uniforme', 'LogNormal', 'Chi2', 'Exponencial', 'Gamma', 'Wald', 'Triang']

    def __init__(símismo, frac_guardar=0.05, args_muestrear=None):
        símismo.frac_guardar = frac_guardar
        símismo._args_muestrear = args_muestrear or {}

    def _calc_calib(símismo, func, dists, n_iter):
        mod_spotpy = ModSpotPy(func=func, dists=dists, inversar=símismo.inversar)

        with tempfile.NamedTemporaryFile('w', encoding='UTF-8', prefix="calibTiko'n_") as d:
            args = dict(spot_setup=mod_spotpy, dbname=d.name, parallel='seq', dbformat='csv', save_sim=False)
            args.update(símismo.args_alg())

            muestreador = símismo.alg_spotpy(**args)

            n = mat.ceil(n_iter * símismo.frac_guardar)

            muestreador.sample(**símismo.args_muestrear(n_iter, n_guardar=n))

            egr_spotpy = pd.read_csv(d.name + '.csv')

        vero = egr_spotpy['like1'].values
        vero, í_buenas = símismo.filtrar_res(vero, n)
        vals = []
        for í in range(len(dists)):
            vals.append(egr_spotpy['parvar_' + str(í)][í_buenas].values)

        return vero, vals

    @property
    def inversar(símismo):
        return False

    @property
    def alg_spotpy(símismo):
        raise NotImplementedError

    def args_alg(símismo):
        return {}

    def args_muestrear(símismo, n_iter, n_guardar):
        args = {'repetitions': n_iter}
        args.update(símismo._args_muestrear)
        return args

    def filtrar_res(símismo, vero, n):
        buenas = np.argpartition(vero, -n)[-n:]
        vero = vero[buenas]
        return vero, buenas


class EVM(CalibSpotPy):
    """Estimación de verosimilitud máxima"""
    alg_spotpy = spt.algorithms.mle


class RS(CalibSpotPy):
    """Recocido Simulado"""
    alg_spotpy = spt.algorithms.sa


class BDD(CalibSpotPy):
    """Búsqueda Dimensionada Dinámicamente"""
    alg_spotpy = spt.algorithms.dds


class CMEDZ(CalibSpotPy):
    """Cadena Markov Evolución Diferencial Z"""
    alg_spotpy = spt.algorithms.demcz


class MC(CalibSpotPy):
    """Monte Carlo"""
    alg_spotpy = spt.algorithms.mc


class MLH(CalibSpotPy):
    alg_spotpy = spt.algorithms.lhs


class CAACAA(CalibSpotPy):
    """Colonia de Abejas Artificial Caótica Ajustada por Aptitud"""

    alg_spotpy = spt.algorithms.fscabc
    inversar = True


class CAA(CalibSpotPy):
    """Colonia de Abejas Artificial"""

    alg_spotpy = spt.algorithms.abc
    inversar = True


class ECBUA(CalibSpotPy):
    """Evolución Compleja Barajada - Universidad de Arizona"""

    alg_spotpy = spt.algorithms.sceua
    inversar = True

    def filtrar_res(símismo, vero, n):
        return vero[-n:], slice(-n, None)

    def args_muestrear(símismo, n_iter, n_guardar):
        args = {'runs_after_convergence': n_guardar}
        args.update(super().args_muestrear(n_iter, n_guardar=n_guardar))
        return args


class ERP(CalibSpotPy):
    """Estimación Robusta de Parámetros"""

    alg_spotpy = spt.algorithms.rope

    def args_alg(símismo):
        return {'alt_objfun': None}


class CMMC(CalibSpotPy):
    """Cadena Markov Monte Carlo"""

    alg_spotpy = spt.algorithms.mcmc

    def filtrar_res(símismo, vero, n):
        return vero[-n:], slice(-n, None)

    def args_muestrear(símismo, n_iter, n_guardar):
        args = {'runs_after_convergence': n_guardar}
        args.update(super().args_muestrear(n_iter, n_guardar=n_guardar))
        return args


class AMAED(CalibSpotPy):
    """Algoritmo Metrópolis Adaptivo de Evolución Diferencial"""

    alg_spotpy = spt.algorithms.dream

    def filtrar_res(símismo, vero, n):
        return vero[-n:], slice(-n, None)

    def args_muestrear(símismo, n_iter, n_guardar):
        args = {'runs_after_convergence': n_guardar}
        args.update(super().args_muestrear(n_iter, n_guardar=n_guardar))
        return args


class ModSpotPy(object):
    def __init__(símismo, func, dists, inversar):
        símismo.func = func
        símismo.dists = dists
        símismo.inversar = inversar

    def parameters(símismo):
        return spt.parameter.generate(
            [_gen_var_spotpy(d.dist, 'var_' + str(í)) for í, d in enumerate(símismo.dists)]
        )

    def simulation(símismo, x):
        for v, d in zip(x, símismo.dists):
            d.prm.val = d.dist.transf_vals(v)

        return símismo.func()

    def evaluation(símismo):
        return  # símismo.res

    def objectivefunction(símismo, simulation, evaluation, params=None):
        return -simulation if símismo.inversar else simulation


def _gen_var_spotpy(dist, nmbr_var):
    nombre_dist = dist.nombre_dist
    paráms = dist.paráms

    ubic = paráms['loc'] if 'loc' in paráms else 0
    escl = paráms['scale'] if 'scale' in paráms else 1

    if nombre_dist == 'Chi2':
        var = spt.parameter.Chisquare(nmbr_var, dt=paráms['df'])

    elif nombre_dist == 'Exponencial':
        var = spt.parameter.Exponential(nmbr_var, scale=escl)

    elif nombre_dist == 'Gamma':
        var = spt.parameter.Gamma(nmbr_var, shape=paráms['a'], scale=escl)

    elif nombre_dist == 'LogNormal':
        var = spt.parameter.logNormal(nmbr_var, mean=ubic, sigma=escl)

    elif nombre_dist == 'Normal':
        var = spt.parameter.Normal(nmbr_var, mean=ubic, stddev=escl)

    elif nombre_dist == 'Uniforme':
        var = spt.parameter.Uniform(nmbr_var, low=ubic, high=ubic + escl)

    else:
        raise ValueError(nombre_dist)

    return var
