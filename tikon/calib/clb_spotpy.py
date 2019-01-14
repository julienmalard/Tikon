import tempfile

import numpy as np
import pandas as pd
import spotpy

from tikon.calib.calibrador import Calibrador


class CalibSpotPy(Calibrador):
    dists_disp = ['Normal', 'Uniforme', 'LogNormal', 'Chi2', 'Exponencial', 'Gamma', 'Wald', 'Weibull', 'Triang']

    @classmethod
    def métodos(cls):
        return ['epm', 'mc', 'cmmc', 'mhl', 'caa', 'dream']

    def _calibrar(símismo, n_iter):

        temp = tempfile.NamedTemporaryFile('w', encoding='UTF-8', prefix="calibTiko'n_")

        mod_spotpy = ModSpotPy(func=símismo.func, paráms=símismo.paráms, dists=símismo.dists)
        muestreador = _algs_spotpy[símismo.método](mod_spotpy, dbname=temp.name, dbformat='csv', save_sim=False)

        if símismo.método == 'dream':
            muestreador.sample(repetitions=2000 + n_iter, runs_after_convergence=n_iter)
        else:
            muestreador.sample(n_iter)
        egr_spotpy = pd.read_csv(temp.name + '.csv')

        probs = egr_spotpy.obt_datos('like1')

        temp.close()

        if símismo.método == 'dream':
            probs = probs[-n_iter:]
            buenas = slice(-n_iter, None)
        else:
            buenas = probs >= np.quantile(probs, 0.95)
            probs = probs[buenas]

        símismo.paráms.guardar_calibs(buenas, probs)


_algs_spotpy = {
    # 'fast': spotpy.algorithms.fast,
    'dream': spotpy.algorithms.dream,
    'mc': spotpy.algorithms.mc,
    'cmmc': spotpy.algorithms.mcmc,

    'epm': spotpy.algorithms.mle,
    'mhl': spotpy.algorithms.lhs,

    # 'sa': spotpy.algorithms.sa,
    # 'sceua': spotpy.algorithms.sceua,
    # 'rope': spotpy.algorithms.rope,
    'caa': spotpy.algorithms.abc,
    # 'fscabc': spotpy.algorithms.fscabc,

}


class ModSpotPy(object):
    def __init__(símismo, func, paráms, dists):
        símismo.func = func
        símismo.paráms = paráms
        símismo.dists = dists

        símismo.res = None

    def parameters(símismo):
        return spotpy.parameter.generate([_gen_spotpy(d) for d in símismo.dists])

    def simulation(símismo, x):
        # para hacer
        for v, p in zip(x, símismo.paráms):
            p.agregar_punto(v)

        símismo.res = símismo.func()
        # return np.mean(símismo.res, axis=1)

    def evaluation(símismo):
        return  # símismo.res

    def objectivefunction(símismo, simulation, evaluation, params=None):
        return símismo.res


def _gen_spotpy(dist, nmbr_var):
    nombre_dist = dist.nombre_dist

    if nombre_dist == 'Chi2':
        raise NotImplementedError
        var = spotpy.parameter.Chisquare(nmbr_var, dt=paráms['df'])

    elif nombre_dist == 'Exponencial':
        var = spotpy.parameter.Exponential(nmbr_var, scale=1)

    elif nombre_dist == 'Gamma':
        raise NotImplementedError
        var = spotpy.parameter.Gamma(nmbr_var, k=paráms['a'])

    elif nombre_dist == 'LogNormal':
        raise NotImplementedError
        var = spotpy.parameter.logNormal(nmbr_var)

    elif nombre_dist == 'Normal':
        var = spotpy.parameter.Normal(nmbr_var, mean=0, stddev=1)

    elif nombre_dist == 'Uniforme':
        var = spotpy.parameter.Uniform(nmbr_var, low=0, high=1)

    elif nombre_dist == 'Weibull':
        raise NotImplementedError
        var = spotpy.parameter.Weibull(nmbr_var)

    else:
        raise ValueError(tipo_dist)
