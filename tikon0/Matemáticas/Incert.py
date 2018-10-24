from warnings import warn as avisar

import numpy as np
import scipy.stats as estad

from tikon0 import __email__ as correo
from tikon0.Matemáticas.Variables import VarSciPy, VarSpotPy

try:
    import pymc3 as pm3
except ImportError:
    pm3 = None

"""
Este código contiene funciones para manejar datos y distribuciones de incertidumbre.
"""


def trazas_a_dists(id_simul, l_d_pm, l_trazas, formato, comunes, l_lms=None, n_rep_parám=None):
    """
    Esta función toma una lista de diccionarios de parámetros y una lista correspondiente de los límites de dichos
    parámetros y genera las distribuciones apriori en formato PyMC, SciPy o NumPy para los parámetros. Devuelve una
    lista de las distribuciones, y también guarda estos variables en los diccionarios de los parámetros bajo la llave
    especificada en id_calib.

    :param id_simul: El nombre de la calibración (para guardar la distribución en el diccionario de cada parámetro).
    :type id_simul: str

    :param l_d_pm: La lista de los diccionarios de los parámetros. Cada diccionario tiene las calibraciones de su
    parámetro.
    :type l_d_pm: list

    :param l_lms: Una lista de los límites de los parámetros, en el mismo orden que l_pm.
    :type l_lms: list

    :param l_trazas: Una lista de cuales trazas incluir. Cada elemento en la lista es una lista de los nombres de las
    calibraciones (trazas) para usar para el parámetro correspondiente en l_pm.
    :type l_trazas: list

    :param formato: El formato de la lista para devolver. Puede se "simul" (NumPy), "calib" (SciPy), o "sensib"
    (SciPy/NumPy).
    :type formato: str

    :param comunes: Si hay que intentar guardar la correspondencia multivarial entre distribuciones generadas por la
    misma calibración
    :type comunes: bool

    :param n_rep_parám: El número de repeticiones paramétricas. Solamente útil, de verdad, para `formato` = "simul".
    :type n_rep_parám: int

    :return: Una lista de las distribuciones generadas, en el mismo orden que l_pm.
    :rtype: list

    """

    # Poner el formato en minúsculas para evitar errores estúpidos
    formato = formato.lower()

    if n_rep_parám is None:
        if formato == 'calib':
            n_rep_parám = 1000  # para hacer: verificar

        else:
            raise ValueError('Se debe especificar el número de repeticiones paramétricas para generar las '
                             'distribuciones NumPy para una simulación.')

    if l_lms is None and formato == 'calib':
        raise ValueError('Hay que especificar los límites teoréticos de las distribuciones para generar a prioris'
                         'PyMC para una calibración.')

    # La lista para guardar las distribuciones generadas, en el mismo orden que la lista de parámetros
    lista_dist = []

    # Generar la lista de los índices para cada traza de cada parámetro
    l_í_trazas = gen_índ_trazas(l_d_pm, l_trazas, n_rep_parám=n_rep_parám, comunes=comunes)

    # Para cada parámetro en la lista...
    for n, d_parám in enumerate(l_d_pm):

        # Una lista de todas las calibraciones aplicables a este parámetro que tienen formato de texto
        trzs_texto = [t for t in l_trazas[n] if t in d_parám and type(d_parám[t]) is str]

        if len(trzs_texto) == 1:
            # Si solamente tenemos una distribución aplicable y esta está en formato de texto...

            if formato == 'calib':
                # Si querremos generar distribuciones para una calibración, generar un variable PyMC directamente.

                # El nombre para el variable PyMC
                nombre_spotpy = 'parám_{}'.format(n)

                # Convertir el texto directamente en distribución
                dist = VarSpotPy.de_texto(texto=d_parám[trzs_texto[0]], nombre=nombre_spotpy)

            elif formato == 'valid':
                # Si querremos una distribución para una validación, generar una traza en NumPy

                # La distribución SciPy
                var_sp = VarSciPy.de_texto(texto=d_parám[trzs_texto[0]])

                # Convertir en matriz NumPy
                dist = var_sp.muestra_alea(n_rep_parám)

            elif formato == 'sensib':
                # Si querremos una distribución para una análisis de sensibilidad, devolver la distribución SciPy
                dist = VarSciPy.de_texto(texto=d_parám[trzs_texto[0]])

            else:
                raise ValueError(formato)

        else:
            # Si tenemos más que una calibración aplicable o esta está en formato de matriz...

            if formato == 'calib':
                # El nombre para el variable PyMC
                nombre_spotpy = 'parám_%i' % n

                # Un vector numpy de la traza de datos para generar la distribución PyMC.
                vec_np = gen_vector_coefs(d_parám=d_parám, í_trazas=l_í_trazas[n])

                # Generar la distribución PyMC
                if usar_pymc3:
                    dist = VarPyMC3.ajust_dist(datos=vec_np, líms=l_lms[n], cont=True, nombre=nombre_spotpy)
                else:
                    dist = VarPyMC2.ajust_dist(datos=vec_np, líms=l_lms[n], cont=True, nombre=nombre_spotpy)

            elif formato == 'valid':
                # En el caso de validación, simplemente querremos una distribución NumPy
                dist = gen_vector_coefs(d_parám=d_parám, í_trazas=l_í_trazas[n])
            elif formato == 'sensib':
                # En el caso de análisis de sensibilidad, querremos una distribución NumPy también
                dist = gen_vector_coefs(d_parám=d_parám, í_trazas=l_í_trazas[n])

        # Guardar la distribución en el diccionario de calibraciones del parámetro
        d_parám[id_simul] = dist

        # Añadir una referencia a la distribución en la lista de distribuciones
        lista_dist.append(dist)

    # Devolver la lista de variables PyMC
    return lista_dist


def gen_índ_trazas(l_d_pm, l_trazas, n_rep_parám, comunes):
    """
    Esta función genera índices de trazas para cada parámetro en una lista de diccionarios de parámetros, tomando
    en cuenta la lista de trazas (calibraciones) que aplican a cada parámetro.

    :param l_d_pm:
    :type l_d_pm: list[dict]

    :param l_trazas:
    :type l_trazas: list[list[str]]

    :param n_rep_parám: El número de índices que querremos.
    :type n_rep_parám: int

    :param comunes:
    :type comunes: bool

    :return:
    :rtype: list[dict[np.ndarray]]
    """

    # Primero, una función que calcula índices de trazas para un diccionario de parámetro.
    def calc_índs(d_trza, l_trza):
        """
        Calcula los índices para un diccionario de parámetro.

        :param d_trza: El diccionario de calibraciones del parámetro
        :type d_trza: dict[str | np.ndarray | VarCalib

        :param l_trza: La lista de distribuciones del parámetro que queremos utilizar
        :type l_trza: list[str]

        :return: Los índices para cada traza (calibración) de este parámetro, en formato de diccionario.
        :rtype: dict[np.ndarray]
        """

        # Calcular el número de repeticiones paramétricas por calibración. Produce una lista, en el mismo orden
        # que calibs, del número de repeticiones para cada calibración.
        n_calibs = len(l_trza)
        rep_per_calib = np.array([n_rep_parám // n_calibs] * n_calibs)

        # Calcular el número que repeticiones que no se dividieron igualmente entre las calibraciones...
        resto = n_rep_parám % n_calibs

        # ...y añadirlas la principio de la lista de calibraciones.
        rep_per_calib[:resto] += 1

        # El diccionario para guardar los índices
        d_índs = {}

        for i, nombre_trz in enumerate(l_trza):
            # Para cada traza en el diccionario...

            # La distribución
            dist = d_trza[nombre_trz]

            if isinstance(dist, str) or isinstance(dist, VarSciPy):
                # Si la distribución está en formato de texto o de distribución SciPy...

                # Solamente guardar el número de repeticiones para esta distribución (índices no tienen sentido).
                d_índs[nombre_trz] = rep_per_calib[i]

            elif isinstance(dist, np.ndarray):
                # Si la distribución está en formato de matriz NumPy...

                # Verificar si la matriz NumPy tiene el tamaño suficiente para el número de repeticiones que querremos
                tamaño_máx = dist.shape[0]
                if tamaño_máx == 0:
                    raise ValueError('Distribución vacía "{}".'.format(nombre_trz))
                if tamaño_máx < rep_per_calib[i]:
                    avisar('Número de repeticiones paramétricas ({}) superior al tamaño de la traza de parámetro '
                           'disponible ({}).'.format(rep_per_calib[i], tamaño_máx))
                    devolv = True
                else:
                    devolv = False

                # Escoger los índices...
                if tamaño_máx == rep_per_calib[i]:
                    # ...en órden original, si estamos tomando la traza entiera (ni más, ni menos). Esto queda
                    # bien importante para no mezclar el orden de las trazas para un análisis de sensibilidad,
                    # donde los valores de los parámetros se determinan por un algoritmo externo.
                    índs = np.arange(tamaño_máx)
                else:
                    # ...sino, de manera aleatoria.
                    índs = np.random.choice(range(tamaño_máx), size=rep_per_calib[i], replace=devolv)
                d_índs[nombre_trz] = índs

            elif isinstance(dist, VarSpotPy):
                # ..y si es un variable de calibración activa, poner el variable sí mismo en la matriz
                d_índs[nombre_trz] = None

            else:
                raise TypeError

        return d_índs

    # Primero, tomamos el caso donde estamos usando distribuciones comunes entre parámetros.
    if comunes:

        # Antes que todo, verificar que los nombres de todas las trazas estén iguales para todos los parámetros.
        # Dado las otras funciones en Tiko'n, no deberia de ser posible tener error aquí. Pero mejor verificar,
        # justo en caso.
        if any(set(x) != set(l_trazas[0]) for x in l_trazas):
            raise ValueError('¡Gran error terrible de programación! Panica primero y depués llama al programador. '
                             '({})'.format(correo))

        # Avisarle al usuario si no será posible de guardar la correspondencia entre todos los parámetos
        if any(type(l_d_pm[0][x]) is str for x in l_trazas):
            avisar('No se podrá guardar la correspondencia entre todas las calibraciones por presencia '
                   'de distribuciones SciPy. La correspondencia sí se guardará para las otras calibraciones.')

        dic_índs = calc_índs(d_trza=l_d_pm[0], l_trza=l_trazas[0])

        l_í_trazas = [dic_índs] * len(l_d_pm)

    else:
        # Ahora, si no trabajamos con distribuciones comunes...
        l_í_trazas = [calc_índs(d_trza=d_p, l_trza=l_trazas[i]) for i, d_p in enumerate(l_d_pm)]

    return l_í_trazas


def gen_vector_coefs(d_parám, í_trazas):
    """
    Esta función genera una matríz de valores posibles para un coeficiente, dado los nombres de las calibraciones
    que queremos usar y el número de repeticiones que queremos.

    :param d_parám: Un diccionario de un parámetro con todas sus calibraciones
    :type d_parám: dict

    :param í_trazas: Un diccionario de los índices a incluir para cada traza. Para trazas en formato de texto,
    únicamente especifica el número de muestras que queremos de la distribución.
    :type í_trazas: dict[int | np.ndarray]

    :return: Una matriz unidimensional con los valores del parámetro.
    :rtype: np.ndarray

    """

    # Un vector vacío para las trazas
    vector = []

    for trz, índs in í_trazas.items():
        # Para cada pareja de traza y de índices..

        if isinstance(d_parám[trz], np.ndarray):
            # Si está en formato NumPy, generar el vector de valores basado en los índices
            vector.append(d_parám[trz][índs])

        elif isinstance(d_parám[trz], str):
            # Si está en formato texto, generar las trazas del tamaño especificado en "índs" por medio de una
            # distribución SciPy
            dist_sp = VarSciPy.de_texto(d_parám[trz])
            vector.append(dist_sp.muestra_alea(n=índs))

        elif isinstance(d_parám[trz], VarSpotPy):
            # Variables de calibraciones activas (PyMC) se agregan directamente
            vector.append(d_parám[trz])

        elif isinstance(d_parám[trz], VarSciPy):
            # Para distribuciones en formato SciPy, generar trazas de una vez
            vector.append(d_parám[trz].muestra_alea(n=índs))

        else:
            # Si la traza era de otro tipo, tenemos un error.
            raise TypeError('Hay un error con la traza, que no puede ser de tipo "{}".'.format(type(d_parám[trz])))

    # Combinar las trazas de cada calibración en una única matriz NumPy unidimensional.
    if len(vector) > 1:
        return np.concatenate(vector)
    else:
        return np.array(vector)


def dists_a_líms(l_dists, por_dist_ingr):
    """
    Esta función genera límites de densidad para cada distribución en una lista de distribuciones.

    :param l_dists: Una lista de las distribuciones
    :type l_dists: list[estad.rv_frozen | np.ndarray]

    :param por_dist_ingr: La fracción de la densidad de la distribución a dejar afuera de los límites
    :type por_dist_ingr: float

    :return: Una lista de los límites, con cada límite sí mismo en formato de lista
    :rtype: list[list[float]]
    """

    # Asegurarse que la lista de distribuciones sea una lista
    if type(l_dists) is not list:
        l_dists = [l_dists]

    # Las superficies de las colas que hay que dejar afuera del rango de los límites
    colas = ((1 - por_dist_ingr) / 2, 0.5 + por_dist_ingr / 2)

    # Inicializar la lista de límites
    l_líms = []

    for dist in l_dists:
        # Para cada distribución...

        # Calcular los porcentiles según el tipo de distribución
        if isinstance(dist, VarSciPy):
            # Para distribuciones SciPy...
            l_líms.append([dist.percentiles(colas[0]), dist.percentiles(colas[1])])

        elif isinstance(dist, np.ndarray):
            # Para distribuciones en formato de matriz NumPy...
            l_líms.append([np.percentile(dist, colas[0] * 100, np.percentile(dist, colas[1] * 100))])

        elif isinstance(dist, str):
            # Para distribuciones en formato de texto...
            d_sp = VarSciPy.de_texto(dist)  # Convertir a SciPy
            l_líms.append([d_sp.percentiles(colas[0]), d_sp.percentiles(colas[1])])  # Calcular los límites

        else:
            # Si no reconocimos el tipo de la distribución, hay un error.
            raise ValueError('Tipo de distribución "{}" no reconocido.'.format(type(dist)))

    return l_líms


def numerizar(f, c=None):
    """
    Esta función toma un diccionaro o una lista de estructura arbitraria y convierte todos
      los objetos adentro en forma numérica. Es particularmente útil para sacar los valores
      de variables de PyMC durante una corrida del modelo.
      Notar que puede tomar diccionarios, listas, listas de diccionarios, diccionarios de listas,
      etc. No mmodifica el objeto original, sino genera una copia.

    :param f: El diccionario o lista para numerizar.
    :type f: dict | list

    :param c: Para recursiones. No especificar al llamar la función.
    :type c: dict | list

    :return: El diccionario o la lista numerizada.
    :rtype: dict | list

    """

    if c is None:
        if type(f) is list:
            c = []
        elif type(f) is dict:
            c = {}

    if type(f) is list:
        for n, v in enumerate(f):
            if type(v) is dict:
                c.append({})
                numerizar(v, c=c[n])
            elif type(v) is list:
                c.append([])
                numerizar(v, c=c[n])
            else:
                c[n] = v.astype(float)

    elif type(f) is dict:
        for ll, v in f.items():

            if type(v) is dict:
                c[ll] = {}
                numerizar(v, c=c[ll])

            elif type(v) is list:
                c[ll] = []
                numerizar(v, c=c[ll])

            else:
                c[ll] = v.astype(float)

    else:
        raise ValueError

    return c


def validar_matr_pred(matr_predic, vector_obs):
    """
    Esta función valida una matriz de predicciones de un variable según los valores observados correspondientes.

    :param matr_predic: La matriz de predicciones. Eje 0 = incertidumbre estocástica, eje 1 = incertidumbre
      paramétrica, eje 2 = día.
    :type matr_predic: np.ndarray

    :param vector_obs: El vector de las observaciones. Eje 0 = día.
    :type vector_obs: np.ndarray

    :return: Devuelve los valores de R2, de RCNEP (Raíz cuadrada normalizada del error promedio), y el R2 de la
    exactitud de los intervalos de confianza (1.0 = exactitud perfecta).
    :rtype: dict
    """

    # Quitar observaciones que faltan
    matr_predic = matr_predic[:, :, ~np.isnan(vector_obs)]
    vector_obs = vector_obs[~np.isnan(vector_obs)]

    # El número de días de predicciones y observaciones
    n_rep_estoc, n_rep_parám, n_días = matr_predic.shape

    # Combinar los dos ejes de incertidumbre (repeticiones estocásticas y paramétricas)
    matr_predic = matr_predic.reshape((n_rep_estoc * n_rep_parám, n_días))

    # Calcular el promedio de todas las repeticiones de predicciones
    vector_predic = matr_predic.mean(axis=0)

    # Calcular R cuadrado
    r2 = calc_r2(vector_predic, vector_obs)

    # Raíz cuadrada normalizada del error promedio
    rcnep = np.divide(np.sqrt(np.square(vector_predic - vector_obs).mean()), np.mean(vector_obs))

    # Validar el intervalo de incertidumbre
    confianza = np.empty_like(vector_obs, dtype=float)
    for n in range(n_días):
        perc = estad.percentileofscore(matr_predic[..., n], vector_obs[n]) / 100
        confianza[n] = abs(0.5 - perc) * 2

    confianza.sort()

    percentiles = np.divide(np.arange(1, n_días + 1), n_días)

    r2_percentiles = calc_r2(confianza, percentiles)

    return {'r2': r2, 'rcnep': rcnep, 'r2_percentiles': r2_percentiles}


def calc_r2(y_obs, y_pred):
    """
    Calcula el coeficiente de determinación (R2) entre las predicciones de un modelo y los valores observados.
    Notar que calcula R2 *entre valores predichos y observados*, y *no* entre un variable predictor y dependiente.
    Para este últimeo, emplear `scipy.stats.linregress`.

    :param y_obs: Valores observados.
    :type y_obs: np.ndarray
    :param y_pred: Valores predichos. (y_sombrero)
    :type y_pred: np.ndarray
    :return: El coeficiente de determinación, R2.
    :rtype: float
    """
    prom_y = np.mean(y_obs)
    sc_rs = np.sum(np.subtract(y_obs, y_pred) ** 2)
    sc_reg = np.sum(np.subtract(y_pred, prom_y) ** 2)
    sc_t = sc_rs + sc_reg

    r2 = 1 - np.divide(sc_rs, sc_t)

    return r2
