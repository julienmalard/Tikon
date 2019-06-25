import math as mat
import tempfile
from warnings import warn as avisar

import numpy as np
import pandas as pd
import spotpy as spt

from tikon.calib.calibrador import Calibrador
from tikon.ecs.dists import DistTraza

_algs_spotpy = {
    'maed': spt.algorithms.dream,
    'mc': spt.algorithms.mc,
    'cmmc': spt.algorithms.mcmc,

    'epm': spt.algorithms.mle,
    'mhl': spt.algorithms.lhs,

    'as': spt.algorithms.sa,
    'sceua': spt.algorithms.sceua,
    'erp': spt.algorithms.rope,
    'caa': spt.algorithms.abc,
    'fscabc': spt.algorithms.fscabc,
    'bdd': spt.algorithms.dds,
    'cmed': spt.algorithms.demcz

}


class CalibSpotPy(Calibrador):
    dists_disp = ['Normal', 'Uniforme', 'LogNormal', 'Chi2', 'Exponencial', 'Gamma', 'Wald', 'Triang']

    métodos = list(_algs_spotpy)

    def calibrar(símismo, n_iter, nombre):

        temp = tempfile.NamedTemporaryFile('w', encoding='UTF-8', prefix="calibTiko'n_")

        mod_spotpy = ModSpotPy(func=símismo.func, dists=símismo.dists,
                               inversar=símismo.método in ['caa', 'fscabc', 'sceua'])
        args = dict(spot_setup=mod_spotpy, dbname=temp.name, parallel='seq', dbformat='csv', save_sim=False)
        if símismo.método != 'erp':
            args['alt_objfun'] = None
        muestreador = _algs_spotpy[símismo.método](**args)
        n = mat.ceil(n_iter / 20)
        if símismo.método in ['maed', 'cmmc', 'sceua']:
            muestreador.sample(repetitions=n_iter, runs_after_convergence=n)
        else:
            muestreador.sample(n_iter)
        egr_spotpy = pd.read_csv(temp.name + '.csv')
        temp.close()

        vero = egr_spotpy['like1'].values
        if símismo.método in ['maed', 'cmmc', 'sceua']:
            vero = vero[-n:]
            buenas = slice(-n, None)
        else:
            buenas = np.argpartition(vero, -n)[-n:]
            vero = vero[buenas]

        if not len(buenas):
            avisar('No se encontró solución aceptable.')
            return

        for í, (dst, vls_prms) in enumerate(símismo.dists.items()):
            vals = egr_spotpy['parvar_' + str(í)][buenas].values
            dist = DistTraza(trz=dst.transf_vals(vals), pesos=vero)
            vls_prms[0].guardar_calib(dist, nombre=nombre)  # para hacer: más elegante


class ModSpotPy(object):
    def __init__(símismo, func, dists, inversar):
        símismo.func = func
        símismo.dists = dists
        símismo.inversar = inversar

    def parameters(símismo):
        return spt.parameter.generate(
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
        return simulation if not símismo.inversar else -simulation


def _gen_spotpy(dist, nmbr_var):
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
