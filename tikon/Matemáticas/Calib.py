import os
import tempfile
from warnings import warn as avisar

import numpy as np
import spotpy
import scipy.stats as estad

from tikon.Matemáticas.Experimentos import BDtexto
from tikon.Matemáticas.Incert import trazas_a_dists
from tikon.Matemáticas.Variables import _inv_logit


class ModCalib(object):
    """
    La clase plantilla (pariente) para modelos de calibración.
    """

    def __init__(símismo, id_calib, lista_d_paráms, método):
        símismo.lista_parám = lista_d_paráms
        símismo.id = id_calib
        símismo.método = método

    def calib(símismo, rep, quema, extraer):
        raise NotImplementedError

    def guardar(símismo, nombre=None):
        raise NotImplementedError


class ModSpotPy(ModCalib):

    def __init__(símismo, función, dic_argums, d_obs, lista_d_paráms, aprioris, lista_líms, id_calib,
                 función_llenar_coefs, método):
        super().__init__(id_calib=id_calib, lista_d_paráms=lista_d_paráms, método=método)

        símismo.paráms = trazas_a_dists(
            id_simul=símismo.id, l_d_pm=lista_d_paráms, l_lms=lista_líms,
            l_trazas=aprioris, formato='calib', comunes=False
        )

        for prm in símismo.paráms:
            prm.modelo = símismo

        # Llenamos las matrices de coeficientes con los variables SpotPy recién creados.
        función_llenar_coefs(nombre_simul=id_calib, n_rep_parám=1, dib_dists=False)

        símismo.func = función
        símismo.args_f = dic_argums
        símismo.d_obs = d_obs

    def calib(símismo, rep, quema, extraer):

        if símismo.método in _algs_spotpy:

            temp = tempfile.NamedTemporaryFile('w', encoding='UTF-8', prefix='CalibTinamït_')

            mod_spotpy = ParaSpotPy(func=símismo.func, args_f=símismo.args_f, paráms=símismo.paráms, obs=símismo.d_obs)

            muestreador = _algs_spotpy[símismo.método](mod_spotpy, dbname=temp.name, dbformat='csv', save_sim=False)

            if símismo.método == 'dream':
                muestreador.sample(repetitions=2000 + rep, runs_after_convergence=rep)
            else:
                muestreador.sample(rep)
            egr_spotpy = BDtexto(temp.name + '.csv')

            cols_prm = [c for c in egr_spotpy.sacar_cols() if c.startswith('par')]
            trzs = np.array([pr._transf_vals(v) for pr, v in zip(símismo.paráms, egr_spotpy.obt_datos(cols_prm))])
            probs = egr_spotpy.obt_datos('like1')

            if os.path.isfile(temp.name + '.csv'):
                os.remove(temp.name + '.csv')

            if símismo.método == 'dream':
                trzs = trzs[-rep:]
                probs = probs[-rep:]
            else:
                buenas = probs >= np.quantile(probs, 0.95)
                trzs = trzs[:, buenas]
                probs = probs[buenas]

            rango_prob = (probs.min(), probs.max())
            pesos = (probs - rango_prob[0]) / (rango_prob[1] - rango_prob[0])

            res = {}
            for i, p in enumerate(símismo.paráms):
                # col_p = ('par' + str(p)).replace(' ', '_')
                p.traza = trzs[i]

            return res

        else:
            raise ValueError('Método de calibración "{}" no reconocido.'.format(símismo.método))

    def guardar(símismo, nombre=None):
        """
        Esta función guarda las trazas de los parámetros generadas por la calibración en el diccionario del parámetro
        como una nueva calibración.

        """

        # Asegurarse de que el nombre de la calibración sea en el formato de texto
        id_calib = str(símismo.id)

        # Si no se especificó nombre, se empleará el mismo nombre que el id de la calibración.
        if nombre is None:
            nombre = símismo.id
        else:
            símismo.id = nombre

        for d_parám in símismo.lista_parám:  # type: dict

            # Para cada parámetro en la lista, convertir el variable SpotPy en un vector numpy de sus trazas, y
            # cambiar el nombre
            vec_np = d_parám[id_calib].traza

            # Quitar el nombre y variable inicial
            d_parám.pop(id_calib)

            # Guardar la traza bajo el nuevo nombre
            d_parám[nombre] = vec_np


_algs_spotpy = {
    'fast': spotpy.algorithms.fast,
    'dream': spotpy.algorithms.dream,
    'mc': spotpy.algorithms.mc,
    'mcmc': spotpy.algorithms.mcmc,
    'mle': spotpy.algorithms.mle,
    'lhs': spotpy.algorithms.lhs,
    'sa': spotpy.algorithms.sa,
    'sceua': spotpy.algorithms.sceua,
    'rope': spotpy.algorithms.rope,
    'abc': spotpy.algorithms.abc,
    'fscabc': spotpy.algorithms.fscabc,

}


class ParaSpotPy(object):
    def __init__(símismo, func, args_f, paráms, obs):
        """

        Parameters
        ----------
        mod : Modelo.Modelo
        líms_paráms : dict
        obs: xr.Dataset
        """

        símismo.paráms = paráms

        símismo.func = func
        símismo.args_f = args_f

        símismo.obs = obs

        símismo.res = None

    def parameters(símismo):
        return spotpy.parameter.generate([p.var for p in símismo.paráms])

    def simulation(símismo, x):
        for v, p in zip(x, símismo.paráms):
            p.val = v

        símismo.res = símismo.func(**símismo.args_f)['d_calib']['Normal']
        return np.mean(símismo.res, axis=1)

    def evaluation(símismo):
        return símismo.obs['Normal']

    def objectivefunction(símismo, simulation, evaluation, params=None):
        # like = spotpy.likelihoods.gaussianLikelihoodMeasErrorOut(evaluation,simulation)

        return _dens_con_pred(evaluation, símismo.res)


def _dens_con_pred(obs, sim):
    res = []
    for s, o in zip(sim, obs):
        d = o*(1+np.exp(-o*2)) / (1-np.exp(-o*2))
        if np.isnan(d):
            d = 1

        s = s / d
        o = o / d
        try:
            res.append(_inv_logit(estad.gaussian_kde(s)(o)[0]))
        except np.linalg.linalg.LinAlgError:
            res.append(1 if o == s[0] else 0)
    return np.mean(res)
