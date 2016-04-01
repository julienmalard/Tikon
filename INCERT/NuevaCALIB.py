import numpy as np
from pymc import deterministic, Gamma, Normal, MCMC

import INCERT.Distribuciones as Ds


class ModBayes(object):
    def __init__(símismo, función, obs, dic_parám, lista_apriori, dic_líms):
        """
        Esta clase merece una descripción detallada. Al fin, un Modelo es lo que trae junto simulación, observaciones y
          parámetros para calibrar estos últimos por medio de inferencia Bayesiana (usando el módulo de Python PyMC).
        Si no conoces bien la inferencia Bayesiana, ahora sería una buena cosa para leer antes de intentar entender lo
          que sigue. Si hacia yo me confundo yo mismo en mi propio código, no lo vas a entender si no entiendes bien
          el concepto de la inferencia Bayesiana con método de Monte Carlo.

        Al inicializarse, un Modelo hace lo siguiente:

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

        :param obs: Una matriz numpy unidimensional con las observaciones. 'función' debe devolver  una matriz
          unidimensional con las predicciones calculadas por el modelo, en el mismo orden, correspondiendo a estas
          observaciones.
        :type obs: np.ndarray

        :param dic_parám: El diccionario de los parámetros para calibrar.
        :type dic_parám: dict

        :param lista_apriori: La lista de los códigos de las calibraciones anteriores a incluir para aproximar las
          distribuciones a priori de los parámetros.
        :type lista_apriori: list

        :param dic_líms: Un diccionario con los límites teoréticos de los parámetros en el modelo. Esto se usa para
          determinar los tipos de funciones apropiados para aproximar las distribuciones a priori de los parámetros.
          (Por ejemplo, no se emplearía una distribución normal para aproximar a un parámetro limitado al rango
          (0, +inf).
        """

        # Guardar una conexión al diccionario de parámetros y crear un número de identificación único para esta
        # calibración.

        símismo.dic_parám = dic_parám
        símismo.id = np.random.uniform()

        # Crear una lista de los objetos estocásticos de PyMC para representar a los parámetros. Esta función
        # también es la responsable para crear la conexión dinámica entre el diccionario de los parámetros y
        # la maquinaría de calibración de PyMC.

        lista_paráms = trazas_a_aprioris(id_calib=símismo.id,
                                         d_pm=dic_parám, d_lms=dic_líms,
                                         lista_apriori=lista_apriori)

        # Una función determinística para llamar a la función de simulación del modelo que estamos calibrando.

        @deterministic
        def simular():
            return función(calib=True)

        # Una distribución normal alrededor de las predicciones del modelo, conectado con las observaciones
        # correspondientes. Para la varianza de la distribución normal, se emplea un tau no informativo.

        tau = Gamma('tau', alpha=0.0001, beta=0.0001)

        dist_obs = Normal('obs', mu=simular, tau=tau, value=obs, observed=True)

        # Y, por fin, el objeto MCMC de PyMC que trae todos estos componientes juntos.

        símismo.MCMC = MCMC(lista_paráms, dist_obs)

    def calib(símismo, rep=10000, quema=100, extraer=10):
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

        símismo.MCMC.sample(iter=rep, burn=quema, thin=extraer)

    def guardar(símismo):
        """
        Esta función guarda las trazas de los parámetros generadas por la calibración en el diccionario del insecto como
          una nueva calibración.
        """
        pymc_a_trazas_tx(d_pm=símismo.dic_parám, id_calib=símismo.id)


class Experimento(object):
    def __init__(símismo):
        pass

    def estab_bd(símismo, archivo):
        pass

    def estab_datos(símismo):
        pass


def trazas_a_aprioris(id_calib, d_pm, d_lms, lista_apriori, i=0, l=None):

    if l is None:
        l = []

    for ll, v in d_pm:
        if type(v) is dict:
            trazas_a_aprioris(id_calib=id_calib, d_pm=v, d_lms=d_lms[ll], lista_apriori=lista_apriori, i=i, l=l)
        elif ll == 'coefs':
            i += 1
            tamaño_mín = min([len(d_pm[tr]) for tr in lista_apriori if type(d_pm[tr]) is np.ndarray])
            traza = []
            for tr in lista_apriori:
                if type(tr) is np.ndarray:
                    traza.append(tr[:tamaño_mín])
                elif type(tr) is str:
                    traza.append(Ds.texto_a_distscipy(tr).rvs(size=tamaño_mín))

            nombre = 'll%i' % i
            dist_apriori = Ds.ajustar_dist(datos=traza, límites=d_lms[ll], cont=True, pymc=True, nombre=nombre)['dist']

            d_pm[id_calib] = dist_apriori
            l += dist_apriori

    return l


def pymc_a_trazas_tx(d_pm, id_calib):

    for ll, v in d_pm:
        if type(v) is dict:
            pymc_a_trazas_tx(d_pm=v, id_calib=id_calib)
        elif ll == str(id_calib):
            d_pm[ll] = v.trace(chain=None)[:]
