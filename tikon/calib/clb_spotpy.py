import tempfile

import numpy as np
import scipy.stats as estad
import spotpy
import pandas as pd

from tikon.calib.calibrador import Calibrador


class CalibSpotPy(Calibrador):

    @classmethod
    def métodos(cls):
        return ['epm']

    def _calibrar(símismo, n_iter):

        temp = tempfile.NamedTemporaryFile('w', encoding='UTF-8', prefix="calibTiko'n_")

        mod_spotpy = ModSpotPy(func=símismo.func, paráms=símismo.paráms)
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
    # 'mc': spotpy.algorithms.mc,
    # 'mcmc': spotpy.algorithms.mcmc,

    'epm': spotpy.algorithms.mle,
    'mhl': spotpy.algorithms.lhs,

    # 'sa': spotpy.algorithms.sa,
    # 'sceua': spotpy.algorithms.sceua,
    # 'rope': spotpy.algorithms.rope,
    # 'abc': spotpy.algorithms.abc,
    # 'fscabc': spotpy.algorithms.fscabc,

}


class ModSpotPy(object):
    def __init__(símismo, func, paráms):
        símismo.func = func
        símismo.paráms = paráms

        símismo.res = None

    def parameters(símismo):
        return spotpy.parameter.generate([p.var for p in símismo.paráms])  # para hacer: arreglar

    def simulation(símismo, x):
        for v, p in zip(x, símismo.paráms):
            p.agregar_punto(v)

        símismo.res = símismo.func()
        # return np.mean(símismo.res, axis=1)

    def evaluation(símismo):
        return símismo.res.obs()

    def objectivefunction(símismo, simulation, evaluation, params=None):
        return _dens_con_pred(evaluation, símismo.res)


def _dens_con_pred(obs, sim):
    res = []
    for s, o in zip(sim, obs):
        d = o * (1 + np.exp(-o * 2)) / (1 - np.exp(-o * 2))
        if np.isnan(d):
            d = 1

        s = s / d
        o = o / d
        try:
            res.append(_logit_inv(estad.gaussian_kde(s)(o)[0]))
        except np.linalg.linalg.LinAlgError:
            res.append(1 if o == s[0] else 0)
    return np.mean(res)


def _logit_inv(x):
    return np.divide(np.exp(x), np.add(np.exp(x), 1))
