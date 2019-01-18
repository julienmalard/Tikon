import math as mat
import tempfile

import numpy as np
import pandas as pd
import spotpy

from tikon.calib.calibrador import Calibrador
from tikon.ecs.dists import DistTraza


class CalibSpotPy(Calibrador):
    dists_disp = ['Normal', 'Uniforme', 'LogNormal', 'Chi2', 'Exponencial', 'Gamma', 'Wald', 'Triang']

    @classmethod
    def métodos(cls):
        return ['epm', 'mc', 'cmmc', 'mhl', 'caa', 'erp', 'dream']

    def _calibrar(símismo, n_iter, nombre):

        temp = tempfile.NamedTemporaryFile('w', encoding='UTF-8', prefix="calibTiko'n_")

        mod_spotpy = ModSpotPy(func=símismo.func, dists=símismo.dists)
        muestreador = _algs_spotpy[símismo.método](mod_spotpy, dbname=temp.name, dbformat='csv', save_sim=False)

        if símismo.método == 'dream':
            muestreador.sample(repetitions=2000 + n_iter, runs_after_convergence=n_iter)
        else:
            muestreador.sample(n_iter)
        egr_spotpy = pd.read_csv(temp.name + '.csv')
        temp.close()

        vero = egr_spotpy['like1'].values
        if símismo.método == 'dream':
            vero = vero[-n_iter:]
            buenas = slice(-n_iter, None)
        else:
            n = mat.ceil(n_iter / 20)
            buenas = np.argpartition(vero, -n)[-n:]
            vero = vero[buenas]

        for í, (dst, vls_prms) in enumerate(símismo.dists.items()):
            vals = egr_spotpy['parvar_' + str(í)][buenas].values
            dist = DistTraza(trz=dst.transf_vals(vals), pesos=vero)
            vls_prms[0].guardar_calib(dist, nombre=nombre)  # para hacer: más elegante


_algs_spotpy = {
    # 'fast': spotpy.algorithms.fast,
    'dream': spotpy.algorithms.dream,
    'mc': spotpy.algorithms.mc,
    'cmmc': spotpy.algorithms.mcmc,

    'epm': spotpy.algorithms.mle,
    'mhl': spotpy.algorithms.lhs,

    # 'sa': spotpy.algorithms.sa,
    # 'sceua': spotpy.algorithms.sceua,
    'erp': spotpy.algorithms.rope,
    'caa': spotpy.algorithms.abc,
    # 'fscabc': spotpy.algorithms.fscabc,

}


class ModSpotPy(object):
    def __init__(símismo, func, dists):
        símismo.func = func
        símismo.dists = dists

    def parameters(símismo):
        return spotpy.parameter.generate(
            [_gen_spotpy(d, 'var_' + str(í)) for í, d in enumerate(símismo.dists)]
        )

    def simulation(símismo, x):
        for v, (d, v_prm) in zip(x, símismo.dists.items()):
            for vl in v_prm:
                vl.poner_val(d.transf_vals(v))

        return símismo.func()
        # return np.mean(símismo.res, axis=1)

    def evaluation(símismo):
        return  # símismo.res

    def objectivefunction(símismo, simulation, evaluation, params=None):
        return simulation


def _gen_spotpy(dist, nmbr_var):
    nombre_dist = dist.nombre_dist
    paráms = dist.paráms

    ubic = paráms['loc'] if 'loc' in paráms else 0
    escl = paráms['scale'] if 'scale' in paráms else 1

    if nombre_dist == 'Chi2':
        var = spotpy.parameter.Chisquare(nmbr_var, dt=paráms['df'])

    elif nombre_dist == 'Exponencial':
        var = spotpy.parameter.Exponential(nmbr_var, scale=escl)

    elif nombre_dist == 'Gamma':
        var = spotpy.parameter.Gamma(nmbr_var, shape=paráms['a'], scale=escl)

    elif nombre_dist == 'LogNormal':
        var = spotpy.parameter.logNormal(nmbr_var, mean=ubic, sigma=escl)

    elif nombre_dist == 'Normal':
        var = spotpy.parameter.Normal(nmbr_var, mean=ubic, stddev=escl)

    elif nombre_dist == 'Uniforme':
        var = spotpy.parameter.Uniform(nmbr_var, low=ubic, high=ubic + escl)

    else:
        raise ValueError(nombre_dist)

    return var
