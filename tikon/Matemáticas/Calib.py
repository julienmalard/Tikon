import numpy as np
import pymc

from tikon.Matemáticas.Incert import trazas_a_dists


class ModBayes(object):
    """
    Esta clase merece una descripción detallada. Al final, un Modelo es lo que trae junto simulación, observaciones y
    parámetros para calibrar estos últimos por medio de inferencia Bayesiana (usando el módulo de Python PyMC).
    Si no conoces bien la inferencia Bayesiana, ahora sería una buena cosa para leer antes de intentar entender lo
    que sigue. Si hacia yo me confundo yo mismo en mi propio código, no lo vas a entender si no entiendes bien
    el concepto de la inferencia Bayesiana con método de Monte Carlo.

    """

    def __init__(símismo, función, dic_argums, d_obs, lista_d_paráms, aprioris, lista_líms, id_calib,
                 función_llenar_coefs):
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

        :param obs:
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

        """

        # Guardar una conexión a la lista de parámetros y crear un número de identificación único para esta
        # calibración.

        símismo.lista_parám = lista_d_paráms
        símismo.id = id_calib
        símismo.n_iter = 0

        # Crear una lista de los objetos estocásticos de PyMC para representar a los parámetros. Esta función
        # también es la responsable para crear la conexión dinámica entre el diccionario de los parámetros y
        # la maquinaría de calibración de PyMC.
        l_var_paráms = trazas_a_dists(id_simul=símismo.id, l_d_pm=lista_d_paráms, l_lms=lista_líms,
                                      l_trazas=aprioris, formato='calib', comunes=False)

        # Incluir también los parientes de cualquier variable determinístico (estos se crean cuando se necesitan
        # transformaciones de las distribuciones básicas de PyMC)
        for parám in l_var_paráms:
            if isinstance(parám, pymc.Deterministic):
                l_var_paráms.append(min(parám.extended_parents))

        # Quitar variables sin incertidumbre. Por una razón muy rara, simul() no funcionará en PyMC sino.
        for parám in l_var_paráms.copy():
            if isinstance(parám, pymc.Uniform):
                if parám.parents['upper'] == parám.parents['lower']:
                    l_var_paráms.remove(parám)
            if isinstance(parám, pymc.Degenerate):
                l_var_paráms.remove(parám)

        # Llenamos las matrices de coeficientes con los variables PyMC recién creados.
        función_llenar_coefs(nombre_simul=id_calib, n_rep_parám=1, dib_dists=False)

        # Una función determinística para llamar a la función de simulación del modelo que estamos calibrando. Le
        # pasamos los argumentos necesarios, si aplican. Hay que incluir los parámetros de la lista l_var_pymc,
        # porque si no PyMC no se dará cuenta de que la función simular() depiende de los otros parámetros y se le
        # olvidará de recalcularla cada vez que cambian los valores de los parámetros.
        @pymc.deterministic(trace=False)
        def simul(d=dic_argums, _=l_var_paráms):
            return función(**d)

        # Ahora, las observaciones
        l_var_obs = []  # Una lista para los variables de observación
        for tipo, m_obs in d_obs.items():
            # Para cada tipo (distribución) de observación y su matriz de observaciones correspondiente...

            # ... crear la distribución apropiada en PyMC
            if tipo == 'Gamma':
                # Si las observaciones siguen una distribución Gamma...

                # Crear el variable PyMC
                var_obs = pymc.Gamma('obs_{}'.format(tipo), alpha=simul['Gamma']['alpha'], beta=simul['Gamma']['beta'],
                                     value=m_obs, observed=True, trace=False)

                # ...y agregarlo a la lista de variables de observación
                l_var_obs.extend([var_obs])

            elif tipo == 'Normal':
                # Si tenemos distribución normal de las observaciones...
                tau = simul['Normal']['sigma'] ** -2
                var_obs = pymc.Normal('obs_{}'.format(tipo), mu=simul['Normal']['mu'], tau=tau,
                                      value=m_obs, observed=True, trace=False)
                nuevos = [var_obs, tau, var_obs.parents['mu'], var_obs.parents['mu'].parents['self'],
                          tau.parents['a'], tau.parents['a'].parents['self']]
                l_var_obs.extend(nuevos)
            else:
                raise ValueError

        # Y, por fin, el objeto MCMC de PyMC que trae todos estos componentes juntos.
        símismo.MCMC = pymc.MCMC({simul, *l_var_paráms, *l_var_obs}, dbname=símismo.id)  # db='sqlite',

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
        símismo.MCMC.use_step_method(pymc.AdaptiveMetropolis, símismo.MCMC.stochastics)

        # Llamar la función "sample" (muestrear) del objeto MCMC de PyMC
        símismo.MCMC.sample(iter=rep, burn=quema, thin=extraer, verbose=1)

    def guardar(símismo, nombre=None):
        """
        Esta función guarda las trazas de los parámetros generadas por la calibración en el diccionario del parámetro
        como una nueva calibración.

        """

        # Asegurarse de que el nombre de la calibración sea en el formato de texto
        id_calib = str(símismo.id)

        # Reabrir la base de datos SQLite
        bd = pymc.database.sqlite.load(id_calib)
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
            except AttributeError:
                vec_np = np.zeros(símismo.n_iter)
                vec_np[:] = d_parám[id_calib].value

            # Quitar el nombre inicial
            d_parám.pop(id_calib)

            # Guardar bajo el nuevo nombre
            d_parám[nombre] = vec_np

        # Cerrar la base de datos de nuevo
        símismo.MCMC.db.close()
