import os
import tempfile
from warnings import warn as avisar

import numpy as np
import scipy.stats as estad
import spotpy

from tikon0.Matemáticas.Experimentos import BDtexto
from tikon0.Matemáticas.Incert import trazas_a_dists
from tikon0.Matemáticas.Variables import _inv_logit


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


class ModBayes(ModCalib):
    """
    Esta clase merece una descripción detallada. Al final, un Modelo es lo que trae junto simulación, observaciones y
    parámetros para calibrar estos últimos por medio de inferencia Bayesiana (usando el módulo de Python PyMC).
    Si no conoces bien la inferencia Bayesiana, ahora sería una buena cosa para leer antes de intentar entender lo
    que sigue. Si hacia yo me confundo yo mismo en mi propio código, no lo vas a entender si no entiendes bien
    el concepto de la inferencia Bayesiana con método de Monte Carlo.

    """

    def __init__(símismo, función, dic_argums, d_obs, lista_d_paráms, aprioris, lista_líms, id_calib,
                 función_llenar_coefs, método):
        """
        Al iniciarse, un Modelo hace el siguiente:

           1. Crea variables estocásticos de PyMC para representar cada parámetro. Para escoger cuál clase de variable
            estocástico (¿distribución normal, gamma, beta, uniforme?) para cada parámetro, usa la función que cabe
            mejor con las informaciones en calibraciones anteriores (especificadas en lista_apriori), siempre consciente
            de los límites físicos de los parámetros tal como especificados en dic_líms (por ejemplo, muchos parámetros,
            como tazas de depredación, no pueden ser negaticas). Todo eso lo hace la función trazas_a_aprioris.
            Lo más interesante es que esa función pone las instancias de variables estocásticos directamente en el
            diccionario de parámetros bajo un número de identificación para esta nueva calibración. Así que, si se
            programa la función de simulación de manera apropiada, los cambios en los parámetros efectuados por PyMC
            durante el proceso de calibración se efectuarán directamente en el modelo que estamos calibrando y no habrá
            necesidad de manualmente cambiar los parámetros de, por ejemplo, cada insecto en la red agroecológica a
            cada paso de calibración. Esto debería de salvar una cantidad importante de tiempo.

           2. Crea una función del tipo pymc.deterministic para llamar a la función de simulación. Esto es la parte
             central de la calibración.

           3. Crea, para cada una de la observaciones, una distribución normal. Se supone entonces que cada valor
             verdadero de las observaciones se ubica en una distribución normal centrada alrededor de la observación.
             Todas estas distribuciones tienen el mismo tau (inverso de la varianza), para cual creamos una
             distribución a priori de Gamma no informativa.

           4. Crea una instancia del objeto MCMC de PyMC, lo cual trae junto parámetros, función de simulación y
             observaciones. Es este objeto que brinda acceso a las funcionalidades de calibración de PyMC.

        :param función: La función para calibrar. En general, eso sería la función 'simular' de un modelo (por ejemplo,
        de una red agroecológica o de un cultivo). Esta función debe de tener un perámetros 'calib' que, en case que
        sea 'True', llamará la versión de esta función apropiada para una calibración (entre otro, que usará
        únicamente los valores de los parámetros tales como especificados por el Modelo y que devolverá los datos
        en formato apropiado).
        :type función: Callable

        :param dic_argums: Un diccionario de los argumentos que hay que pasar a "función". Si no hay argumentos para
        pasar, poner un diccionario vacío, {}.
        :type dic_argums: dict

        :param d_obs:
        :type d_obs: dict[dict[np.ndarray]]

        :param lista_d_paráms: El diccionario de los parámetros para calibrar.
        :type lista_d_paráms: list

        :param aprioris: La lista de los códigos de las calibraciones anteriores a incluir para aproximar las
        distribuciones a priori de los parámetros.
        :type aprioris: list

        :param lista_líms: Una lista con los límites teoréticos de los parámetros en el modelo. Esto se usa para
        determinar los tipos de funciones apropiados para aproximar las distribuciones a priori de los parámetros.
        (Por ejemplo, no se emplearía una distribución normal para aproximar un parámetro limitado al rango
        (0, +inf).
        :type lista_líms: list

        :param id_calib: El nombre para identificar la calibración.
        :type id_calib: str

        :param función_llenar_coefs: Una funcion que llenara los diccionarios del Simulable con los coeficientes PyMC
          recién creados.
        :type función_llenar_coefs: Callable

        :param método:
        :type método: str

        """

        # Guardar una conexión a la lista de parámetros y crear un número de identificación único para esta
        # calibración.

        super().__init__(id_calib=id_calib, lista_d_paráms=lista_d_paráms, método=método)
        símismo.n_iter = 0

        # Crear una lista de los objetos estocásticos de PyMC para representar los parámetros. Esta función
        # también es la responsable de crear la conexión dinámica entre el diccionario de los parámetros y
        # la maquinaria de calibración de PyMC.
        l_var_paráms = trazas_a_dists(id_simul=símismo.id, l_d_pm=lista_d_paráms, l_lms=lista_líms,
                                      l_trazas=aprioris, formato='calib', comunes=False)

        # Crear una lista de los variables "finales" de los parámetros
        l_vars_pymc = [v.var for v in l_var_paráms]

        # Un variable de prueba
        vacío_2 = pm2.Normal('vacío_2', 0, 1)
        l_vars_pymc.append(vacío_2)

        # Llenamos las matrices de coeficientes con los variables PyMC recién creados.
        función_llenar_coefs(nombre_simul=id_calib, n_rep_parám=1, dib_dists=False)

        # Una función determinística para llamar a la función de simulación del modelo que estamos calibrando. Le
        # pasamos los argumentos necesarios, si aplican. Hay que incluir los parámetros de la lista l_var_pymc,
        # porque si no PyMC no se dará cuenta de que la función simular() depiende de los otros parámetros y se le
        # olvidará de recalcularla cada vez que cambian los valores de los parámetros.

        # Para hacer: formalizar
        avisar('Código experimental--¡¡probablemente no funcional!!')

        # err_temp = [VarPyMC2('error_mu_{}'.format(x), tipo_dist='Gamma', paráms={'a': 1, 'escl': 1, 'ubic': 0})
        #             for x in range(12)]
        # l_err_temp = [v.var for v in err_temp]
        # n_mem = [VarPyMC2('n_mem_error_{}'.format(x), tipo_dist='Gamma', paráms={'a': 1, 'escl': 10, 'ubic': 1})
        #          for x in range(12)]
        # l_n_mem = [v.var for v in n_mem]
        # l_vars_err = l_err_temp + l_n_mem
        #
        # def calc_err(mu, mag, n_mem, n_etps=12):
        #     e = np.zeros_like(mu, dtype=float)
        #     tam = len(mu) // n_etps
        #
        #     for n in range(mu.shape[0]):
        #
        #         rest = n % tam
        #         div = n // tam
        #
        #         mem = n_mem[div]
        #         mitad_mem = mem / 2
        #
        #         if rest <= mitad_mem:
        #             lím_inf = div * tam
        #             lím_sup = div * tam + mem
        #
        #         elif rest >= tam - mitad_mem:
        #             lím_inf = (div + 1) * tam - mem - 1
        #             lím_sup = (div + 1) * tam - 1
        #         else:
        #             lím_inf = n - mitad_mem
        #             lím_sup = n + mitad_mem
        #
        #         lím_inf = np.maximum(lím_inf, div * tam)
        #         lím_sup = np.minimum(lím_sup, (div+1) * tam - 1)
        #
        #         máx_preds = np.max(mu[mat.ceil(lím_inf):mat.floor(lím_sup) + 1])
        #         mín_preds = np.min(mu[mat.ceil(lím_inf):mat.floor(lím_sup) + 1])
        #
        #         if lím_inf != int(lím_inf):
        #             val_lím_inf = np.interp(lím_inf, range(mu.shape[0]), mu)
        #             máx_preds = max(máx_preds, val_lím_inf)
        #             mín_preds = min(mín_preds, val_lím_inf)
        #
        #         if lím_sup != int(lím_sup):
        #             val_lím_sup = np.interp(lím_sup, range(mu.shape[0]), mu)
        #             máx_preds = max(máx_preds, val_lím_sup)
        #             mín_preds = min(mín_preds, val_lím_sup)
        #
        #         rango_preds = np.maximum(0, máx_preds - mín_preds)
        #
        #         e[n] = rango_preds * mag[div]
        #
        #     return np.maximum(e, 1)

        # fin de para hacer: formalizar

        # res = función(**dic_argums)

        @pm2.deterministic(trace=False)
        def simul(_=l_vars_pymc, d=d_obs):
            res = función(**dic_argums)
            return res

        var_error = VarPyMC2('error_mod', tipo_dist='Gamma', paráms={'a': 1, 'escl': .01, 'ubic': 0})

        # var_error = pm2.Gamma('error_mod', alpha=1, beta=1/0.1)
        #
        @pm2.deterministic(trace=False)
        def calc_tau_mod(r=simul, ve=var_error.var):
            #     return 1 / float(var_error)**2
            return 1 / np.maximum(1, (var_error * r['Normal']['mu']) ** 2)

        #
        # @pm2.deterministic(trace=False)
        # def calc_error_temp(r=simul, e=l_err_temp, n=l_n_mem, d=d_obs, ve=var_error):
        #
        #     error = calc_err(r['Normal']['mu'], mag=err_temp, n_mem=n_mem)
        #     return error

        # Ahora, las observaciones
        l_var_obs = []  # Una lista para los variables de observación
        for tipo, m_obs in d_obs.items():
            # Para cada tipo (distribución) de observación y su matriz de observaciones correspondiente...

            # ... crear la distribución apropiada en PyMC
            if tipo == 'Gamma':
                # Si las observaciones siguen una distribución Gamma...

                # Crear el variable PyMC
                var_obs = pm2.Gamma('obs_{}'.format(tipo), alpha=simul['Gamma']['alpha'],
                                    beta=simul['Gamma']['beta'],
                                    value=m_obs, observed=True, trace=False)

                # ...y agregarlo a la lista de variables de observación
                l_var_obs.extend([var_obs])

            elif tipo == 'Normal':
                # Si tenemos distribución normal de las observaciones...
                #
                # mu_final = pm2.Normal('mu_final', mu=mu, tau=calc_tau_mod, trace=False)

                # tau = simul['Normal']['sigma'] ** -2
                tau = pm2.HalfNormal('mitau', tau=1e6)
                # mu = pm2.Normal('mu_error', mu=simul['Normal']['mu'], tau=tau, trace=False)
                var_obs = pm2.Normal('obs_{}'.format(tipo),
                                     # mu=mu_final,
                                     tau=calc_tau_mod,
                                     mu=simul['Normal']['mu'],
                                     value=m_obs, observed=True, trace=False)

                nuevos = [var_obs,
                          tau,
                          # mu,
                          # mu_final,
                          # var_obs.parents['mu'],
                          # tau.parents['a'], tau.parents['a'].parents['self']
                          ]
                l_var_obs.extend(nuevos)
            else:
                raise ValueError

        # Otro variable de prueba
        vacío_0 = pm2.Normal('vacío_0', 0, 1)

        # Y, por fin, el objeto MCMC de PyMC que trae todos estos componentes juntos.
        símismo.MCMC = pm2.MCMC({simul,
                                 #                                      calc_error_temp,
                                 calc_tau_mod,
                                 # var_error.var,
                                 *l_vars_pymc[0:1],
                                 var_error.var,
                                 #                                      *l_vars_err,
                                 *l_var_obs, vacío_0, vacío_2},
                                db='sqlite',
                                dbname=símismo.id,
                                dbmode='w')

    def calib(símismo, rep, quema, extraer):
        """
        Esta función sirve para llamar a las funcionalidades de calibración de PyMC.

        :param rep: El número de repeticiones para la calibración.
        :type rep: int

        :param quema: El número de repeticiones iniciales a cortar de los resultados. Esto evita que los resultados
        estén muy influenciados por los valores iniciales (y posiblemente erróneos) que toman los parámetros al
        principio de la calibración.
        :type quema: int

        :param extraer: Cada cuántas repeticiones hay que guardar para los resultados. Por ejemplo, con `extraer`=10,
        cada 10 repeticiones se guardará, así que, con `rep`=10000, `quema`=100 y `extraer`=10, quedaremos con trazas
        de (10000 - 100) / 10 = 990 datos para aproximar la destribución de cada parámetro.

        """

        símismo.n_iter += rep

        # Utilizar el algoritmo Metrópolis Adaptivo para la calibración. Sería probablemente mejor utilizar NUTS, pero
        # para eso tendría que implementar pymc3 aquí y de verdad no quiero.
        if símismo.método.lower() == 'metrópolis adaptivo':
            símismo.MCMC.use_step_method(pm2.AdaptiveMetropolis, símismo.MCMC.stochastics,
                                         delay=200, interval=200,
                                         greedy=False, shrink_if_necessary=True, verbose=4
                                         )
        elif símismo.método.lower() == 'metrópolis':
            pass
        else:
            raise ValueError

        # Llamar la función "sample" (muestrear) del objeto MCMC de PyMC
        símismo.MCMC.sample(iter=rep, burn=quema, thin=extraer, verbose=1, tune_interval=10)


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
        d = o * (1 + np.exp(-o * 2)) / (1 - np.exp(-o * 2))
        if np.isnan(d):
            d = 1

        s = s / d
        o = o / d
        try:
            res.append(_inv_logit(estad.gaussian_kde(s)(o)[0]))
        except np.linalg.linalg.LinAlgError:
            res.append(1 if o == s[0] else 0)
    return np.mean(res)
