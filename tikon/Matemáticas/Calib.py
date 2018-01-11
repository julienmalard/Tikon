from tempfile import mkdtemp
from warnings import warn as avisar

import numpy as np
import pymc as pm2
import pymc3 as pm3
import theano.tensor as tt
from pymc3.step_methods import smc as mcs
from theano.compile.ops import as_op

import tikon.Matemáticas.Distribuciones as Ds
from tikon.Controles import usar_pymc3
from tikon.Matemáticas.Incert import trazas_a_dists


class ModCalib(object):
    """
    La clase plantilla (pariente) para modelos de calibración.
    """

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

        símismo.lista_parám = lista_d_paráms
        símismo.id = id_calib
        símismo.método = método
        símismo.n_iter = 0

        if not usar_pymc3:

            # Crear una lista de los objetos estocásticos de PyMC para representar a los parámetros. Esta función
            # también es la responsable para crear la conexión dinámica entre el diccionario de los parámetros y
            # la maquinaría de calibración de PyMC.
            l_var_paráms = trazas_a_dists(id_simul=símismo.id, l_d_pm=lista_d_paráms, l_lms=lista_líms,
                                          l_trazas=aprioris, formato='calib', comunes=False)

            # Quitar variables sin incertidumbre. Sino, por una razón muy rara, simul() no funcionará en PyMC.
            l_var_paráms_final = []
            for v in l_var_paráms:
                if isinstance(v, pm2.Uniform) or isinstance(v, pm2.Degenerate):
                    continue
                if any(isinstance(p, pm2.Degenerate) for p in list(v.extended_parents)):
                    continue
                if any(isinstance(p, pm2.Uniform) and p.parents['upper'] == p.parents['lower']
                       for p in list(v.extended_parents)):
                    continue
                l_var_paráms_final.append(v)

                if isinstance(v, pm2.Deterministic) or isinstance(v, pm2.Lambda):
                    l_var_paráms_final += (list(v.extended_parents))

            # Llenamos las matrices de coeficientes con los variables PyMC recién creados.
            función_llenar_coefs(nombre_simul=id_calib, n_rep_parám=1, dib_dists=False)

            # Una función determinística para llamar a la función de simulación del modelo que estamos calibrando. Le
            # pasamos los argumentos necesarios, si aplican. Hay que incluir los parámetros de la lista l_var_pymc,
            # porque si no PyMC no se dará cuenta de que la función simular() depiende de los otros parámetros y se le
            # olvidará de recalcularla cada vez que cambian los valores de los parámetros.
            @pm2.deterministic(trace=False)
            def simul(_=l_var_paráms_final):
                return función(**dic_argums)

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
                    tau = simul['Normal']['sigma'] ** -2
                    var_obs = pm2.Normal('obs_{}'.format(tipo), mu=simul['Normal']['mu'], tau=tau,
                                         value=m_obs, observed=True, trace=False)
                    nuevos = [var_obs, tau, var_obs.parents['mu'], var_obs.parents['mu'].parents['self'],
                              tau.parents['a'], tau.parents['a'].parents['self']]
                    l_var_obs.extend(nuevos)
                else:
                    raise ValueError

            # Y, por fin, el objeto MCMC de PyMC que trae todos estos componentes juntos.
            símismo.MCMC = pm2.MCMC({simul, *l_var_paráms_final, *l_var_obs}, db='sqlite', dbname=símismo.id,
                                    dbmode='w')
        else:

            símismo.MCMC = pm3.Model()

            with símismo.MCMC as mod:
                # Crear una lista de los objetos estocásticos de PyMC para representar a los parámetros. Esta función
                # también es la responsable para crear la conexión dinámica entre el diccionario de los parámetros y
                # la maquinaría de calibración de PyMC.
                l_var_paráms = trazas_a_dists(id_simul=símismo.id, l_d_pm=lista_d_paráms, l_lms=lista_líms,
                                              l_trazas=aprioris, formato='calib', comunes=False)

                # Llenamos las matrices de coeficientes con los variables PyMC recién creados.
                función_llenar_coefs(nombre_simul=id_calib, n_rep_parám=1, dib_dists=False)

                # Una función determinística para llamar a la función de simulación del modelo que estamos calibrando. Le
                # pasamos los argumentos necesarios, si aplican. Hay que incluir los parámetros de la lista l_var_pymc,
                # porque si no PyMC no se dará cuenta de que la función simular() depiende de los otros parámetros y se le
                # olvidará de recalcularla cada vez que cambian los valores de los parámetros.
                @as_op(itypes=[tt.fscalar] * len(l_var_paráms), otypes=[tt.fscalar])
                def simul(_=l_var_paráms):
                    return función(**dic_argums)

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
                        tau = simul['Normal']['sigma'] ** -2
                        var_obs = pm2.Normal('obs_{}'.format(tipo), mu=simul['Normal']['mu'], tau=tau,
                                             value=m_obs, observed=True, trace=False)
                        nuevos = [var_obs, tau, var_obs.parents['mu'], var_obs.parents['mu'].parents['self'],
                                  tau.parents['a'], tau.parents['a'].parents['self']]
                        l_var_obs.extend(nuevos)
                    else:
                        raise ValueError

                # Y, por fin, el objeto MCMC de PyMC que trae todos estos componentes juntos.
                símismo.MCMC = pm2.MCMC({simul, *l_var_paráms, *l_var_obs}, db='sqlite', dbname=símismo.id,
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

        if not usar_pymc3:
            # Utilizar el algoritmo Metrópolis Adaptivo para la calibración. Sería probablemente mejor utilizar NUTS, pero
            # para eso tendría que implementar pymc3 aquí y de verdad no quiero.
            if símismo.método.lower() == 'metrópolis adaptivo':
                símismo.MCMC.use_step_method(pm2.AdaptiveMetropolis, símismo.MCMC.stochastics)
            elif símismo.método.lower() == 'metrópolis':
                pass
            else:
                raise ValueError

            # Llamar la función "sample" (muestrear) del objeto MCMC de PyMC
            símismo.MCMC.sample(iter=rep, burn=quema, thin=extraer, verbose=1)

        else:
            if símismo.método.lower() == 'mcs':
                n_trazas = 1
                dir_temp = mkdtemp(prefix='TKN_MCS')
                traza = mcs.sample_smc(n_steps=rep,
                                       n_chains=n_trazas,
                                       progressbar=False,
                                       homepath=dir_temp,
                                       stage=0,
                                       random_seed=42)

    def guardar(símismo, nombre=None):
        """
        Esta función guarda las trazas de los parámetros generadas por la calibración en el diccionario del parámetro
        como una nueva calibración.

        """

        # Asegurarse de que el nombre de la calibración sea en el formato de texto
        id_calib = str(símismo.id)

        # Reabrir la base de datos SQLite
        bd = pm2.database.sqlite.load(id_calib)
        bd.connect_model(símismo.MCMC)

        # Si no se especificó nombre, se empleará el mismo nombre que el id de la calibración.
        if nombre is None:
            nombre = símismo.id
        else:
            símismo.id = nombre

        for d_parám in símismo.lista_parám:  # type: dict

            # Para cada parámetro en la lista, convertir el variable PyMC en un vector numpy de sus trazas, y
            # cambiar el nombre
            try:
                vec_np = d_parám[id_calib].trace(chain=None)[:]
            except (AttributeError, IndexError):
                vec_np = np.zeros(símismo.n_iter)
                vec_np[:] = d_parám[id_calib].value

            # Quitar el nombre inicial
            d_parám.pop(id_calib)

            # Guardar bajo el nuevo nombre
            d_parám[nombre] = vec_np

        # Cerrar la base de datos de nuevo
        símismo.MCMC.db.close()


class ModGLUE(ModCalib):

    def __init__(símismo):
        raise NotImplementedError

    def calib(símismo, rep, quema, extraer):
        raise NotImplementedError

    def guardar(símismo, nombre=None):
        raise NotImplementedError


class VarCalib(object):
    def __init__(símismo, nombre, tipo_dist, paráms):
        """

        :param nombre:
        :type nombre: str
        :param tipo_dist: El tipo de distribución. (P.ej., ``Normal``, ``Uniforme``, etc.)
        :type tipo_dist: str
        :param paráms:
        :type paráms: dict
        """

        símismo.nombre = nombre
        símismo.tipo_dist = tipo_dist
        símismo.paráms = paráms
        símismo.var = NotImplemented

    def obt_var(símismo):
        """

        :return:
        :rtype: list | pm2.Stochastic | pm3.model.FreeRV
        """
        raise NotImplementedError

    def obt_val(símismo):
        """

        :return:
        :rtype: float
        """
        raise NotImplementedError

    def dibujar(símismo, ejes):
        raise NotImplementedError

    def traza(símismo):
        """

        :return:
        :rtype: np.ndarray
        """
        raise NotImplementedError


class VarPyMC2(VarCalib):
    """
    Esta clase representa variables de PyMC v2.
    """

    def __init__(símismo, nombre, tipo_dist, paráms):
        """

        :param nombre:
        :type nombre: str
        :param tipo_calib:
        :type tipo_calib:
        :param tipo_dist:
        :type tipo_dist: str
        :param paráms:
        :type paráms: dict
        """

        super().__init__(nombre=nombre, tipo_dist=tipo_dist, paráms=paráms)

        # Verificar que existe este variable
        if tipo_dist not in Ds.dists:
            raise ValueError('La distribución %s no existe en la base de datos de Tikon para distribuciones PyMC2.' %
                             tipo_dist)

        # Generar la distribución y sus parámetros
        transform = {'mult': 1, 'sum': 0}

        if tipo_dist == 'Beta':
            clase_dist = pm2.Beta
            paráms_pymc = (paráms[0], paráms[1])
            transform['sum'] = paráms[2]
            transform['mult'] = paráms[3]

        elif tipo_dist == 'Cauchy':
            clase_dist = pm2.Cauchy
            paráms_pymc = (paráms[0], paráms[1])

        elif tipo_dist == 'Chi2':
            clase_dist = pm2.Chi2
            paráms_pymc = (paráms[0],)
            transform['sum'] = paráms[1]
            transform['mult'] = paráms[2]

        elif tipo_dist == 'Exponencial':
            clase_dist = pm2.Exponential
            paráms_pymc = (1 / paráms[1],)
            transform['sum'] = paráms[0]

        elif tipo_dist == 'WeibullExponencial':
            clase_dist = pm2.Exponweib
            paráms_pymc = (paráms[0], paráms[1], paráms[2], paráms[3])

        elif tipo_dist == 'Gamma':
            clase_dist = pm2.Gamma
            paráms_pymc = (paráms[0], 1 / paráms[2])
            transform['sum'] = paráms[1]

        elif tipo_dist == 'MitadCauchy':
            clase_dist = pm2.HalfCauchy
            paráms_pymc = (paráms[0], paráms[1])

        elif tipo_dist == 'MitadNormal':
            clase_dist = pm2.HalfNormal
            paráms_pymc = (1 / paráms[1] ** 2,)
            transform['sum'] = paráms[0]

        elif tipo_dist == 'GammaInversa':
            clase_dist = pm2.InverseGamma
            paráms_pymc = (paráms[0], paráms[2])
            transform['sum'] = paráms[1]

        elif tipo_dist == 'Laplace':
            clase_dist = pm2.Laplace
            paráms_pymc = (paráms[0], 1 / paráms[1])

        elif tipo_dist == 'Logística':
            clase_dist = pm2.Logistic
            paráms_pymc = (paráms[0], 1 / paráms[1])

        elif tipo_dist == 'LogNormal':
            clase_dist = pm2.Lognormal
            paráms_pymc = (np.log(paráms[2]), 1 / (paráms[0] ** 2))
            transform['mult'] = paráms[2]
            transform['sum'] = paráms[1]

        elif tipo_dist == 'TNoCentral':
            clase_dist = pm2.NoncentralT
            paráms_pymc = (paráms[2], 1 / paráms[3], paráms[0])

        elif tipo_dist == 'Normal':
            clase_dist = pm2.Normal
            paráms_pymc = (paráms[0], 1 / paráms[1] ** 2)

        elif tipo_dist == 'Pareto':
            clase_dist = pm2.Pareto
            paráms_pymc = (paráms[0], paráms[2])
            transform['sum'] = paráms[1]

        elif tipo_dist == 'T':
            clase_dist = pm2.T
            paráms_pymc = (paráms[0],)
            transform['sum'] = paráms[1]
            transform['mult'] = 1 / np.sqrt(paráms[2])

        elif tipo_dist == 'NormalTrunc':
            clase_dist = pm2.TruncatedNormal
            mu = paráms[2]
            mín, máx = min(paráms[0], paráms[1]), max(paráms[0], paráms[1])  # SciPy, aparamente, los puede inversar
            paráms_pymc = (mu, 1 / paráms[3] ** 2, mín * paráms[3] + mu, máx * paráms[3] + mu)

        elif tipo_dist == 'Uniforme':
            clase_dist = pm2.Uniform
            # Normalizar la distribución Uniforme para PyMC. Sino hace muchos problemas.
            paráms_pymc = (0, 1)
            transform['sum'] = paráms[0]
            transform['mult'] = paráms[1]

        elif tipo_dist == 'VonMises':
            clase_dist = pm2.VonMises
            paráms_pymc = (paráms[1], paráms[0])
            transform['mult'] = paráms[2]

        elif tipo_dist == 'Weibull':
            clase_dist = pm2.Weibull
            raise NotImplementedError  # Para hacer: implementar la distrubución Weibull (minweibull en SciPy)

        elif tipo_dist == 'Bernoulli':
            clase_dist = pm2.Bernoulli
            paráms_pymc = (paráms[0],)
            transform['sum'] = paráms[1]

        elif tipo_dist == 'Binomial':
            clase_dist = pm2.Binomial
            paráms_pymc = (paráms[0], paráms[1])
            transform['sum'] = paráms[2]

        elif tipo_dist == 'Geométrica':
            clase_dist = pm2.Geometric
            paráms_pymc = (paráms[0],)
            transform['sum'] = paráms[1]

        elif tipo_dist == 'Hypergeométrica':
            clase_dist = pm2.Hypergeometric
            paráms_pymc = (paráms[1], paráms[0], paráms[2])
            transform['sum'] = paráms[3]

        elif tipo_dist == 'BinomialNegativo':
            clase_dist = pm2.NegativeBinomial
            paráms_pymc = (paráms[1], paráms[0])
            transform['sum'] = paráms[2]

        elif tipo_dist == 'Poisson':
            clase_dist = pm2.Poisson
            paráms_pymc = (paráms[0],)
            transform['sum'] = paráms[1]

        elif tipo_dist == 'UnifDiscr':
            clase_dist = pm2.DiscreteUniform
            paráms_pymc = (paráms[0], paráms[1] - 1)

        else:
            raise ValueError('La distribución "{}" existe en la base de datos de Tiko\'n para distribuciones PyMC2,'
                             'pero no está configurada en la clase VarPyMC2.'.format(tipo_dist))

        # Crear el variable PyMC2
        var_base = clase_dist(paráms_pymc)
        símismo.l_vars = l_vars = [var_base]

        # Hacer modificaciones, si necesario, y agregar éstas a la lista de variables.
        if transform['mult'] != 1:
            dist_2 = pm2.Lambda('%s_m' % nombre, lambda x=var_base, m=transform['mult']: x * m)

            var_base.keep_trace = False  # No guardar la traza del variable pariente
            l_vars.append(dist_2)

        if transform['sum'] != 0:
            dist_3 = pm2.Lambda('%s_s' % nombre, lambda x=l_vars[-1], s=transform['sum']: x + s)

            l_vars[-1].keep_trace = False  # No guardar la traza del variable pariente
            l_vars.append(dist_3)

        # Guardar el último variable de la lista como variable principal.
        símismo.var = l_vars[-1]

    def obt_val(símismo):
        return float(símismo.var.value)

    def obt_var(símismo):

        v_base = símismo.l_vars[0]

        if isinstance(v_base, pm2.Degenerate):
            return []
        elif isinstance(v_base, pm2.Uniform) and v_base.parents['upper'] == v_base.parents['lower']:
            return []
        else:
            return [v for v in símismo.l_vars if not (v.rand() == v.rand() == v.rand())]

    def dibujar(símismo, ejes):

        n = 10000
        if len(símismo.l_vars) == 1:
            puntos = np.array([símismo.var.rand() for _ in range(n)])
        else:
            dist_stoc = símismo.l_vars[0]
            puntos = np.array([(dist_stoc.rand(), símismo.var.value)[1] for _ in range(n)])

        y, delim = np.histogram(puntos, normed=True, bins=n // 100)
        x = 0.5 * (delim[1:] + delim[:-1])

        ejes[0].plot(x, y, 'b-', lw=2, alpha=0.6)
        ejes[0].set_title('Distribución')

        ejes[1].plot(símismo.traza())
        ejes[1].set_title('Traza')

    def traza(símismo):

        try:
            return símismo.var.trace(chain=None)[:]
        except AttributeError:
            return np.array([])


class VarPyMC3(VarCalib):
    def __init__(símismo, nombre, tipo_dist, paráms):
        super().__init__(nombre=nombre, tipo_dist=tipo_dist, paráms=paráms)

        if pm3 is None:
            raise ImportError(
                'PyMC 3 (pymc3) no está instalado en esta máquina.\nDeberías de instalarlo un día. De verdad que'
                'es muy chévere.')

        símismo.traza_modelo = None

        transform_pymc = {'mult': 1, 'sum': 0}

        if tipo_dist == 'Beta':
            dist = pm3.Beta(nombre=nombre, alpha=paráms['a'], beta=paráms['b'])
            a_priori = pm3.Beta.dist(alpha=paráms['a'], beta=paráms['b'])
            transform_pymc['mult'] = paráms['scale']
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'Cauchy':
            dist = pm3.Cauchy(nombre=nombre, alpha=paráms['a'], beta=paráms['scale'])
            a_priori = pm3.Cauchy.dist(alpha=paráms['a'], beta=paráms['scale'])

        elif tipo_dist == 'Chi2':
            dist = pm3.ChiSquared(nombre=nombre, nu=paráms['df'])
            a_priori = pm3.ChiSquared.dist(nu=paráms['df'])
            transform_pymc['mult'] = paráms['scale']
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'Exponencial':
            dist = pm3.Exponential(nombre=nombre, lam=1 / paráms['scale'])
            a_priori = pm3.Exponential.dist(lam=1 / paráms['scale'])
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'Gamma':
            dist = pm3.Gamma(nombre=nombre, alpha=paráms['alpha'], beta=1 / paráms['scale'])
            a_priori = pm3.Gamma.dist(alpha=paráms['alpha'], beta=1 / paráms['scale'])
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'MitadCauchy':
            dist = pm3.HalfCauchy(nombre=nombre, beta=paráms['scale'])
            a_priori = pm3.HalfCauchy.dist(beta=paráms['scale'])
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'MitadNormal':
            dist = pm3.HalfNormal(nombre=nombre, sd=paráms['scale'])
            a_priori = pm3.HalfNormal.dist(sd=paráms['scale'])
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'GammaInversa':
            dist = pm3.InverseGamma(nombre=nombre, alpha=paráms['a'], beta=paráms['scale'])
            a_priori = pm3.InverseGamma.dist(alpha=paráms['a'], beta=paráms['scale'])
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'Laplace':
            dist = pm3.Laplace(nombre=nombre, mu=paráms['loc'], b=paráms['scale'])
            a_priori = pm3.Laplace.dist(mu=paráms['loc'], b=paráms['scale'])

        elif tipo_dist == 'Logística':
            dist = pm3.Logistic(nombre=nombre, mu=paráms['loc'], s=paráms['scale'])
            a_priori = pm3.Logistic.dist(mu=paráms['loc'], s=paráms['scale'])

        elif tipo_dist == 'LogNormal':
            dist = pm3.Lognormal(nombre=nombre, mu=paráms['loc'], sd=paráms['scale'])  # para hacer: verificar
            a_priori = pm3.Lognormal.dist(mu=paráms['loc'], sd=paráms['scale'])  # para hacer: verificar

        elif tipo_dist == 'Normal':
            dist = pm3.Normal(nombre=nombre, mu=paráms['loc'], sd=paráms['scale'])
            a_priori = pm3.Normal.dist(mu=paráms['loc'], sd=paráms['scale'])

        elif tipo_dist == 'Pareto':
            dist = pm3.Pareto(nombre=nombre, alpha=paráms['b'], m=paráms['scale'])  # para hacer: verificar
            a_priori = pm3.Pareto.dist(alpha=paráms['b'], m=paráms['scale'])  # para hacer: verificar

        elif tipo_dist == 'T':
            dist = pm3.StudentT(nombre=nombre, nu=paráms['df'], mu=paráms['loc'], sd=paráms['scale'])  # para hacer: verificar
            a_priori = pm3.StudentT.dist(nu=paráms['df'], mu=paráms['loc'], sd=paráms['scale'])  # para hacer: verificar

        elif tipo_dist == 'NormalTrunc':
            mín, máx = min(paráms[0], paráms[1]), max(paráms[0], paráms[1])  # SciPy, aparamente, los puede inversar
            mín_abs, máx_abs = mín * paráms['scale'] + paráms['mu'], máx * paráms['scale'] + paráms['mu']
            NormalTrunc = pm3.Bound(pm3.Normal, lower=mín_abs, upper=máx_abs)
            dist = NormalTrunc(nombre=nombre, mu=paráms['loc'], sd=paráms['scale'])
            a_priori = NormalTrunc.dist(mu=paráms['loc'], sd=paráms['scale'])

        elif tipo_dist == 'Uniforme':
            dist = pm3.Uniform(nombre=nombre, lower=paráms['loc'], upper=paráms['loc'] + paráms['scale'])
            a_priori = pm3.Uniform.dist(lower=paráms['loc'], upper=paráms['loc'] + paráms['scale'])

        elif tipo_dist == 'VonMises':
            dist = pm3.VonMises(nombre=nombre, mu=paráms['loc'], kappa=paráms['kappa'])
            a_priori = pm3.VonMises.dist(mu=paráms['loc'], kappa=paráms['kappa'])
            transform_pymc['mult'] = paráms['scale']

        elif tipo_dist == 'Weibull':
            raise NotImplementedError  # Para hacer: implementar la distrubución Weibull (minweibull en SciPy)
            dist = pm3.Weibull()
            a_priori = pm3.Weibull.dist()

        elif tipo_dist == 'Bernoulli':
            dist = pm3.Bernoulli(nombre=nombre, p=paráms['p'])
            a_priori = pm3.Bernoulli.dist(p=paráms['p'])
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'Binomial':
            dist = pm3.Binomial(nombre=nombre, n=paráms['n'], p=paráms['p'])
            a_priori = pm3.Binomial.dist(n=paráms['n'], p=paráms['p'])
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'Geométrica':
            dist = pm3.Geometric(nombre=nombre, p=paráms['p'])
            a_priori = pm3.Geometric.dist(p=paráms['p'])
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'BinomialNegativo':
            n = paráms['n']
            p = paráms['p']
            dist = pm3.NegativeBinomial(nombre=nombre, mu=n(1 - p) / p, alpha=n)
            a_priori = pm3.NegativeBinomial.dist(mu=n(1 - p) / p, alpha=n)
            avisar('Tenemos que verificar esta distribución')  # para hacer: verificar
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'Poisson':
            dist = pm3.Poisson(nombre=nombre, mu=paráms['mu'])
            a_priori = pm3.Poisson.dist(mu=paráms['mu'])
            transform_pymc['sum'] = paráms['loc']

        elif tipo_dist == 'UnifDiscr':
            dist = pm3.DiscreteUniform(nombre=nombre, lower=paráms['low'], upper=paráms['high'])
            a_priori = pm3.DiscreteUniform.dist(lower=paráms['low'], upper=paráms['high'])
            transform_pymc['sum'] = paráms['loc']

        else:
            raise ValueError(
                'La distribución %s no existe en la base de datos de Tiko\'n para distribuciones de PyMC 3.' %
                tipo_dist)

        # Hacer modificaciones, si necesario.
        if transform['mult'] != 1:
            a_priori = None
            if transform['sum'] == 0:
                dist = pm3.Deterministic('{}_m'.format(nombre), dist * transform['mult'])
            else:
                dist = pm3.Deterministic('{}_m_s'.format(nombre), dist * transform['mult'] + transform['sum'])
        elif transform['sum'] != 0:
            dist = pm3.Deterministic('{}_s'.format(nombre), dist + transform['sum'])

        # Guardar el variable
        símismo.var = dist

        # Guardar la distribución a priori (para gráficos).
        símismo.a_priori = a_priori

    def obt_val(símismo):
        raise NotImplementedError('')

    def obt_var(símismo):
        return símismo.var

    def dibujar(símismo, ejes):
        trz = símismo.traza_modelo
        if trz is None:
            raise ValueError('Todavía no se ha hecho una calibración con este variable.')

        pm3.traceplot(trace=trz, varnames=símismo.nombre, priors=[símismo.a_priori], ax=ejes)

    def traza(símismo):

        trz = símismo.traza_modelo

        if trz is None:
            return []
        else:
            return trz.get_values(símismo.var)
