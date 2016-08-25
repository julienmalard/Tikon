import numpy as np
from pymc import deterministic, stochastic, Exponential, Normal, MCMC

import Matemáticas.NuevoIncert as Incert


class ModBayes(object):
    """
    Esta clase merece una descripción detallada. Al fin, un Modelo es lo que trae junto simulación, observaciones y
      parámetros para calibrar estos últimos por medio de inferencia Bayesiana (usando el módulo de Python PyMC).
    Si no conoces bien la inferencia Bayesiana, ahora sería una buena cosa para leer antes de intentar entender lo
      que sigue. Si hacia yo me confundo yo mismo en mi propio código, no lo vas a entender si no entiendes bien
      el concepto de la inferencia Bayesiana con método de Monte Carlo.

    """

    def __init__(símismo, función, dic_argums, obs, lista_paráms, aprioris, lista_líms, id_calib, función_llenar_coefs):
        """
        Al iniciarse, un Modelo hace lo siguiente:

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
        :type función: function

        :param dic_argums: Un diccionario de los argumentos que hay que pasar a "función". Si no hay argumentos para
          pasar, poner un diccionario vacío, {}.
        :type dic_argums: dict

        :param obs: Una matriz numpy unidimensional con las observaciones. 'función' debe devolver  una matriz
          unidimensional con las predicciones calculadas por el modelo, en el mismo orden, correspondiendo a estas
          observaciones.
        :type obs: np.ndarray

        :param lista_paráms: El diccionario de los parámetros para calibrar.
        :type lista_paráms: list

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
        :type función_llenar_coefs: function

        """

        # Guardar una conexión a la lista de parámetros y crear un número de identificación único para esta
        # calibración.

        símismo.lista_parám = lista_paráms
        símismo.id = id_calib

        # Crear una lista de los objetos estocásticos de PyMC para representar a los parámetros. Esta función
        # también es la responsable para crear la conexión dinámica entre el diccionario de los parámetros y
        # la maquinaría de calibración de PyMC.

        lista_paráms = trazas_a_aprioris(id_calib=símismo.id,
                                         l_pm=lista_paráms, l_lms=lista_líms,
                                         aprioris=aprioris)

        # Llenamos las matrices de coeficientes con los variables PyMC recién creados
        función_llenar_coefs(n_rep_parám=1, calibs=id_calib, usar_especificados=True, comunes=False)

        # Para la varianza de la distribución normal, se emplea un tau no informativo.
        tau = Exponential('tau', beta=1e-10)

        # Una función determinística para llamar a la función de simulación del modelo que estamos calibrando. Le
        # pasamos los argumentos necesarios, si aplican.
        @deterministic(plot=False)
        def simular(d=dic_argums, t=tau):
            return función(**d)

        # Una distribución normal alrededor de las predicciones del modelo, conectado con las observaciones
        # correspondientes.
        dist_obs = Normal('obs', mu=simular, tau=tau, value=obs, observed=True)

        # Y, por fin, el objeto MCMC de PyMC que trae todos estos componientes juntos.
        símismo.MCMC = MCMC({dist_obs, tau, simular, *lista_paráms})

    def calib(símismo, rep, quema, extraer):
        """
        Esta función sirve para llamar a las funcionalidades de calibración de PyMC.

        :param rep: El número de repeticiones para la calibración.
        :type rep: int

        :param quema: El número de repeticiones iniciales a cortar de los resultados. Esto evita que los resultados
          estén muy influenciados por los valores iniciales (y posiblemente erróneos) que toman los parámetros al
          principio de la calibración.
        :type quema: int

        :param extraer: Cada cuántas repeticiones hay que guardar para los resultados. Por ejemplo, con extraer=10,
          cada 10 repeticiones se guardará

        Por ejemplo, con rep=10000, quema=100 y extraer=10, quedaremos con trazas de (10000 - 100) / 10 = 990 datos
          para aproximar la destribución de cada parámetro.

        """

        # Llamar la función "sample" del objeto MCMC de PyMC
        símismo.MCMC.sample(iter=rep, burn=quema, thin=extraer, verbose=1)
        prueba = símismo.MCMC.trace('simular')[:]

    def guardar(símismo):
        """
        Esta función guarda las trazas de los parámetros generadas por la calibración en el diccionario del parámetro
          como una nueva calibración.

        """

        # Asegurarse de que el nombre de la calibración sea en el formato de texto
        id_calib = str(símismo.id)

        for d_parám in símismo.lista_parám:

            # Para cada parámetro en la lista, convertir el variable PyMC en un vector numpy de sus trazas.
            d_parám[id_calib] = d_parám[id_calib].trace(chain=None)[:]


def trazas_a_aprioris(id_calib, l_pm, l_lms, aprioris):
    """
    Esta función toma una lista de diccionarios de parámetros y una lista correspondiente de los límites de dichos
      parámetros y genera las distribuciones apriori PyMC para los parámetros. Devuelve una lista de los variables
      PyMC, y también guarda estos variables en los diccionarios de los parámetros bajo la llave especificada en
      id_calib.

    :param id_calib: El nombre de la calibración (para guardar el variable PyMC en el diccionario de cada parámetro).
    :type id_calib: str

    :param l_pm: La lista de los diccionarios de los parámetros. Cada diccionario tiene las calibraciones de su
      parámetro.
    :type l_pm: list

    :param l_lms: Una lista de los límites de los parámetros, en el mismo orden que l_pm.
    :type l_lms: list

    :param aprioris: Una lista de cuales distribuciones incluir en la calibración. Cada elemento en la lista
      es una lista de los nombres de las calibraciones para usar para el parámetro correspondiente en l_pm.
    :type aprioris: list

    :return: Una lista de los variables PyMC generados, en el mismo orden que l_pm.
    :rtype: list

    """

    # La lista para guardar las distribuciones de PyMC, en el mismo orden que la lista de parámetros
    lista_dist = []

    # Para cada parámetro en la lista...
    for n, d_parám in enumerate(l_pm):

        # El nombre para el variable PyMC
        nombre = 'parám_%i' % n

        # Si el usuario especificó una distribución a priori, usarla. Sino, usar la lista de aprioris general.
        if 'especificado' in d_parám:
            calibs = ['especificado']
        else:
            calibs = aprioris

        # La distribución pymc del a priori
        dist_apriori = None

        # Si solo hay una calibración para aplicar y es en formato de distribución, intentar y ver si no se puede
        # convertir directamente en distribución pymc.
        if len(calibs) == 1 and type(d_parám[calibs[0]] is str):
            dist_apriori = Incert.texto_a_dist(texto=d_parám[calibs[0]], usar_pymc=True, nombre=nombre)

        # Si todavía no tenemos nuestra distribución a priori, generarla por aproximación.
        if dist_apriori is None:
            # Un vector numpy de la traza de datos para generar la distribución PyMC
            traza = Incert.gen_vector_coefs(dic_parám=d_parám, calibs=calibs, n_rep_parám=200)

            # Generar la distribución PyMC
            dist_apriori = Incert.ajustar_dist(datos=traza, límites=l_lms[n], cont=True,
                                               usar_pymc=True, nombre=nombre)[0]

        # Guardar el variable PyMC en el diccionario de calibraciones del parámetro
        d_parám[id_calib] = dist_apriori

        # Añadir una referencia al variable PyMC en la lista de distribuciones
        lista_dist.append(dist_apriori)

    # Devolver la lista de variables PyMC
    return lista_dist
