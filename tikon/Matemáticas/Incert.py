import ast
import math as mat
from warnings import warn as avisar

import numpy as np
import pymc as pm2
import scipy.stats as estad
from scipy.optimize import minimize as minimizar

from tikon.Matemáticas import Distribuciones as Ds
from tikon import __email__ as correo
from tikon.Controles import usar_pymc3

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
                nombre_pymc = 'parám_{}'.format(n)

                # Convertir el texto directamente en distribución
                if usar_pymc3:
                    dist = VarPyMC3.de_texto(texto=d_parám[trzs_texto[0]], nombre=nombre_pymc)
                else:
                    dist = VarPyMC2.de_texto(texto=d_parám[trzs_texto[0]], nombre=nombre_pymc)

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
                raise ValueError

        else:
            # Si tenemos más que una calibración aplicable o esta está en formato de matriz...

            if formato == 'calib':
                # El nombre para el variable PyMC
                nombre_pymc = 'parám_%i' % n

                # Un vector numpy de la traza de datos para generar la distribución PyMC.
                vec_np = gen_vector_coefs(d_parám=d_parám, í_trazas=l_í_trazas[n])

                # Generar la distribución PyMC
                if usar_pymc3:
                    dist = VarPyMC2.ajust_dist(datos=vec_np, líms=l_lms[n], cont=True, nombre=nombre_pymc)
                else:
                    dist = VarPyMC2.ajust_dist(datos=vec_np, líms=l_lms[n], cont=True, nombre=nombre_pymc)

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

            elif isinstance(dist, VarCalib):
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

        elif isinstance(d_parám[trz], VarCalib):
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
    :rtype: (float, float, float)
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


# Clases de variables
class VarAlea(object):
    def __init__(símismo, tipo_dist, paráms, nombre=None):
        """

        :param tipo_dist:
        :type tipo_dist: str
        :param paráms:
        :type paráms: dict
        :param nombre:
        :type nombre: str
        """

        if tipo_dist not in símismo.dists_disp():
            raise ValueError('La distribución "{}" no está implementada para el tipo de variable "{}".'
                             .format(tipo_dist, símismo.__class__.__name__))

        símismo.tipo_dist = tipo_dist
        símismo.paráms = paráms
        símismo.nombre = nombre

    def a_texto(símismo):
        """
        Esta función devuelve una representación de texto en formato de Tiko'n para la distribución.

        :return: La versión texto de la distribución.
        :rtype: str

        """

        texto_dist = '%s~(%s)' % (símismo.nombre, str(símismo.paráms))

        return texto_dist

    @classmethod
    def de_texto(cls, texto, nombre=None):

        # Primero, decidimos si tenemos una especificación de distribución por nombre o por rango (y densidad)
        if '~' in texto:
            # Si tenemos especificación por nombre...
            return cls.de_texto_dist(texto, nombre=nombre)
        else:
            # Si tenemos especificación por rango (y/o densidad):

            # Formato general: "(0, 1); 0.85en(0, 0.05)" o "(0, 1)"

            if ';' in texto:
                líms, txt_dens = texto.split(';')
                líms = tuple(float(x) for x in líms.strip('()').split(','))

                prcnt, líms_dens = txt_dens.split('en')
                prcnt = float(prcnt)
                líms_dens = tuple(float(x) for x in líms_dens.strip('()').split(','))

                if prcnt == 100:
                    return cls.de_líms(líms_dens, cont=True, nombre=nombre)
                else:
                    return cls.de_densidad(dens=prcnt, líms_dens=líms_dens, líms=líms, cont=True,
                                           nombre=nombre)

            else:
                líms = tuple(float(x) for x in texto.strip('()').split(','))

                return cls.de_líms(líms, cont=True, nombre=nombre)

    @classmethod
    def ajust_dist(cls, datos, líms, cont, lista_dist=None, nombre=None):
        """
        Esta función, tomando las límites teoréticas de una distribución y una serie de datos proveniendo de dicha
        distribución, escoge la distribución más apropriada y ajusta sus parámetros.

        :param datos: Un vector de valores del parámetro
        :type datos: np.ndarray

        :param cont: Determina si la distribución es contínua (en vez de discreta)
        :type cont: bool

        :param líms: Las límites teoréticas de la distribucion (p. ej., (0, np.inf), (-np.inf, np.inf), etc.)
        :type líms: tuple

        :param nombre: El nombre del variable, si vamos a generar un variable de PyMC
        :type nombre: str

        :param lista_dist: Una lista de los nombres de distribuciones a considerar. dist=None las considerará todas.
        :type lista_dist: list

        :return: Distribución PyMC o de Scipy su ajuste (p)
        :rtype: VarAlea

        """

        if lista_dist is None:
            lista_dist = cls.dists_disp()

        resultado = cls._ajust_dist(datos=datos, líms=líms, cont=cont, nombre=nombre,
                                    lista_dist=lista_dist)
        if resultado['p'] <= 0.10:
            avisar('El ajuste de la mejor distribución quedó muy mal (p = %f).' % round(resultado['p'], 4))

        return resultado['dist']

    @classmethod
    def de_densidad(cls, dens, líms_dens, líms, cont, nombre=None):
        """
        Esta función genera distribuciones estadísticas dado un rango de valores y la densidad de
        probabilidad en este rango, además de las límites intrínsicas del parámetro.

        :param líms_dens: Un rango de valores.
        :type líms_dens: tuple

        :param dens: La probabilidad de que el variable se encuentre a dentro del rango.
        :type dens: float

        :param líms: Los límites intrínsicos del parámetro.
        :type líms: tuple

        :param cont: Indica si la distribución es una distribución contínua o discreta.
        :type cont: bool

        :param nombre: El nombre de la distribución (se emplea únicamente para variables PyMC).
        :type nombre: str

        :return: Una distribución con las características deseadas.
        :rtype: VarAlea

        """
        raise NotImplementedError

    @classmethod
    def _ajust_dist(cls, datos, líms, cont, lista_dist, nombre=None):
        """

        :param datos:
        :type datos:
        :param líms:
        :type líms:
        :param cont:
        :type cont:
        :param lista_dist:
        :type lista_dist:
        :param nombre:
        :type nombre:
        :return:
        :rtype: dict
        """
        raise NotImplementedError

    @classmethod
    def de_líms(cls, líms, cont, nombre):
        raise NotImplementedError

    @classmethod
    def de_texto_dist(cls, texto, nombre=None):

        # Dividir el nombre de la distribución de sus parámetros.
        tipo_dist, paráms = texto.split('~')
        paráms = ast.literal_eval(paráms)

        return cls(tipo_dist=tipo_dist, paráms=paráms, nombre=nombre)

    @classmethod
    def de_scipy(cls, dist_scipy, nombre):

        tipo_dist = NotImplemented
        paráms = NotImplemented

        return cls(nombre=nombre, tipo_dist=tipo_dist, paráms=paráms)

    @staticmethod
    def dists_disp():
        """
        Devuelve una lista de los nombres de distribuciones disponibles para este tipo de variable.
        :return: La lista de distribuciones posibles.
        :rtype: list[str]
        """
        raise NotImplementedError


class VarSciPy(VarAlea):

    def __init__(símismo, tipo_dist, paráms):
        """

        :param tipo_dist:
        :type tipo_dist: str
        :param paráms:
        :type paráms: dict
        """
        super().__init__(tipo_dist=tipo_dist, paráms=paráms)

        símismo.mult = 1

        paráms = paráms.copy()
        if 'ubic' in paráms:
            paráms['loc'] = paráms.pop('ubic')
        if 'escl' in paráms:
            paráms['scale'] = paráms.pop('escl')

        # Transformaciones manuales a la escala de la distribución.
        símismo.suma = 0
        if paráms['scale'] == 0:
            símismo.mult = 0
            símismo.suma = paráms['loc']
            paráms['scale'] = 1
        elif paráms['scale'] < 0:
            símismo.mult = -paráms['scale']

            paráms['scale'] = -paráms['scale']
            paráms['loc'] = -paráms['ubic']

        símismo.var = Ds.dists[tipo_dist]['scipy'](**paráms)

    def percentiles(símismo, q):
        return símismo.var.ppf(q * símismo.mult)

    def muestra_alea(símismo, n):
        return símismo.var.rvs(n) * símismo.mult + símismo.suma

    def fdp(símismo, x):
        return símismo.var.pdf(x / símismo.mult)

    def dibujar(símismo, ejes):

        n = 10000
        puntos = símismo.muestra_alea(n)

        y, delim = np.histogram(puntos, normed=True, bins=n // 100)
        x = 0.5 * (delim[1:] + delim[:-1])

        ejes.plot(x, y, 'b-', lw=2, alpha=0.6)
        ejes.set_title('Distribución')

    @classmethod
    def de_densidad(cls, dens, líms_dens, líms, cont, nombre=None):

        # La precisión que querremos de nuestras distribuciones aproximadas
        límite_precisión = 0.0001

        # Leer los límites intrínsicos del parámetro
        mín = líms[0]
        máx = líms[1]

        # Si el rango está al revés, arreglarlo.
        if líms_dens[0] > líms_dens[1]:
            líms_dens = (líms_dens[1], líms_dens[0])

        # Asegurarse de que el rango cabe en los límites
        if líms_dens[0] < mín or líms_dens[1] > máx:
            raise ValueError('El rango tiene que caber entre los límites teoréticos del variable.')

        # Si no decimos el contrario, no invertiremos la distribución.
        inv = False

        if dens == 1:
            # Si no hay incertidumbre, usar una distribución uniforme entre el rango.
            if cont:
                tipo_dist = 'Uniforme'
                paráms = {'ubic': líms_dens[0], 'escl': (líms_dens[1] - líms_dens[0])}
            else:
                tipo_dist = 'UnifDiscr'
                paráms = {'low': líms_dens[0], 'high': líms_dens[1] + 1}

        else:
            # Si hay incertidumbre...

            # Primero, hay que asegurarse que el máximo y mínimo del rango no sean iguales
            if líms_dens[0] == líms_dens[1]:
                raise ValueError('Un rango para una distribucion con certidumbre inferior a 1 no puede tener valores '
                                 'mínimos y máximos iguales.')

            # Una idea de la escala del rango de incertidumbre
            # Para hacer: ¿utilizar distribuciones exponenciales para escalas grandes?
            # escala_rango = líms_dens[1] - líms_dens[0]

            # Invertir distribuciones en (-inf, R]
            if mín == -np.inf and máx != np.inf:
                mín = -máx
                máx = np.inf
                inv = True

            # Ahora, asignar una distribución según cada caso posible
            if mín == -np.inf:
                if máx == np.inf:  # El caso (-inf, +inf)
                    if cont:
                        mu = np.average(líms_dens)
                        # Calcular sigma por dividir el rango por el inverso (bilateral) de la distribución cumulativa.
                        sigma = ((líms_dens[1] - líms_dens[0]) / 2) / estad.norm.ppf((1 - dens) / 2 + dens)
                        tipo_dist = 'Normal'
                        paráms = {'ubic': mu, 'escl': sigma}
                    else:
                        raise ValueError(
                            'No se pueden especificar a prioris con niveles de certidumbre inferiores a 100% '
                            'con parámetros discretos en el rango (-inf, +inf).')

                else:  # El caso (-np.inf, R)
                    raise ValueError('Debería ser imposible llegar a este error en Tiko\'n.')

            else:
                if máx == np.inf:  # El caso [R, +inf)
                    if cont:

                        # Primero vamos a intentar crear una distribución gamma con la densidad especificada
                        # (certidumbre) entre el rango especificado y 50% de la densidad no especificada de cada
                        # lado del rango (así asegurándose que la densidad esté más o menos bien distribuida a través
                        # del rango).

                        área_cola = (1 - dens) / 2  # La densidad que querremos de cada lado (cola) del rango

                        # La función de optimización.
                        def calc_ajust_gamma_1(x):
                            """
                            Emplea un rango normalizado y toma como único argumento el parámetro a de la distribución
                            gamma; devuelve el ajuste de la distribución.

                            :param x: una matriz NumPy con los parámetros para calibrar. x[0] = a
                            :type x: np.ndarray

                            :return: El ajust del modelo
                            :rtype: float
                            """

                            # Primero, calcular dónde hay que ponder el límite inferior para tener la densidad querrida
                            # a la izquierda de este límite.
                            mín_ajust = estad.gamma.ppf(área_cola, a=x[0])

                            # Ahora, calcular el límite superior proporcional (según el rango y límite teorético
                            # especificados).
                            máx_ajust = mín_ajust / (líms_dens[0] - mín) * (líms_dens[1] - mín)

                            # Calcular a cuál punto la densidad abajo del rango superior coincide con la densidad
                            # deseada.
                            ajust = abs(estad.gamma.cdf(máx_ajust, a=x[0]) - (1 - área_cola))

                            return ajust  # Devolver el ajuste del modelo.

                        # Hacer la optimización
                        opt = minimizar(calc_ajust_gamma_1, x0=np.array([1]),
                                        bounds=[(1, None)])

                        # Calcular la escala
                        escala = (líms_dens[0] - mín) / estad.gamma.ppf(área_cola, a=opt.x[0])

                        # Calcular los parámetros
                        tp_paráms = [opt.x[0], mín, escala]

                        # Validar la optimización
                        valid = abs(
                            (estad.gamma.cdf(líms_dens[1], a=tp_paráms[0], loc=tp_paráms[1], scale=tp_paráms[2]) -
                             estad.gamma.cdf(líms_dens[0], a=tp_paráms[0], loc=tp_paráms[1], scale=tp_paráms[2])) -
                            dens)

                        # Si validó bien, todo está bien.
                        if valid < límite_precisión:
                            tipo_dist = 'Gamma'
                            paráms = {'a': tp_paráms[0], 'ubic': tp_paráms[1], 'escl': tp_paráms[2]}

                        else:
                            # Si no validó bien, intentaremos otra cosa. Ahora vamos a permitir que el límite inferior
                            # de la distribución gamma cambie un poco.
                            # Esto puede ayudar en casos donde rango[1] - rango[0] << rango[0] - mín

                            def calc_ajust_gamma_2(x):
                                """
                                Emplea un rango normalizado; devuelve el ajuste de la distribución.

                                :param x: una matriz NumPy con los parámetros para calibrar. x[0] = a, x[1] = loc.
                                :type x: np.ndarray

                                :return: El ajust del modelo
                                :rtype: float
                                """

                                # Primero, calcular dónde hay que ponder el límite inferior para tener la densidad querrida
                                # a la izquierda de este límite.
                                mín_ajust = estad.gamma.ppf(área_cola, a=x[0], loc=x[1])

                                # Ahora, calcular el límite superior proporcional (según el rango y límite teorético
                                # especificados).
                                máx_ajust = mín_ajust / (líms_dens[0] - mín) * (líms_dens[1] - mín)

                                # Calcular a cuál punto la densidad abajo del rango superior coincide con la densidad
                                # deseada.
                                ajust = abs(estad.gamma.cdf(máx_ajust, a=x[0], loc=x[1]) - (1 - área_cola))

                                return ajust

                            opt = minimizar(calc_ajust_gamma_2, x0=np.array([1, mín]),
                                            bounds=[(1, None), (mín, None)])

                            escala = (líms_dens[0] - mín) / estad.gamma.ppf(área_cola, a=opt.x[0], loc=opt.x[1])

                            tp_paráms = [opt.x[0], opt.x[1] * escala + mín, escala]

                            # Validar que todo esté bien.
                            valid = abs(
                                (estad.gamma.cdf(líms_dens[1], a=tp_paráms[0], loc=tp_paráms[1], scale=tp_paráms[2]) -
                                 estad.gamma.cdf(líms_dens[0], a=tp_paráms[0], loc=tp_paráms[1], scale=tp_paráms[2])) -
                                dens)

                            if valid < límite_precisión:
                                # Si está bien, allí guardamos el resultado.
                                tipo_dist = 'Gamma'
                                paráms = {'a': tp_paráms[0], 'ubic': tp_paráms[1], 'escl': tp_paráms[2]}

                            else:
                                # Si todavía logramos encontrar una buena distribución, reconocemos que no podemos hacer
                                # milagros y abandonamos la condición que las dos colas deben tener el mismo área.
                                # Siempre guardamos el mínimo de la función gamma en mín (el mínimo teorético del
                                # parámetro especificado por el usuario).
                                # Esto puede ayudar en casos donde rango[0] - mín << rango[1] - mín y certidumbre >> 0.

                                # OTRA función de optimización...
                                mx_ajust = 5  # 5 es un buen número para evitar problemas.

                                def calc_ajust_gamma_3(x):
                                    """
                                    Emplea un rango normalizado y toma como único argumento el parámetro a de la
                                    distribución gamma; devuelve el ajuste de la distribución.

                                    :param x: x[0] es el parámetro a de la distribución gamma, y x[1] la escala de la
                                    distribución.
                                    :type x: np.ndarray

                                    :return: El ajust del modelo
                                    :rtype: float

                                    """

                                    máx_ajust = mx_ajust  # El rango superior

                                    # El rango inferior proporcional
                                    mín_ajust = (líms_dens[0] - mín) * máx_ajust / (líms_dens[1] - mín)

                                    # La densidad de la distribución abajo del límite inferior del rango
                                    dens_sup = 1 - estad.gamma.cdf(máx_ajust, a=x[0], scale=x[1])

                                    # La densidad adentro de los límites del rango
                                    dens_líms = estad.gamma.cdf(máx_ajust, a=x[0], scale=x[1]) - \
                                                estad.gamma.cdf(mín_ajust, a=x[0], scale=x[1])

                                    # Devolver una medida del ajuste de la distribución. Lo más importante sería la
                                    # densidad adentro del rango, pero también la densidad en la cola superior.
                                    return abs(dens_líms - dens) * 100 + abs(dens_sup - área_cola)

                                opt = minimizar(calc_ajust_gamma_3, x0=np.array([2, 1]),
                                                bounds=[(1, None), (1e-10, None)])

                                tp_paráms = [opt.x[0], mín, (líms_dens[1] - mín) / mx_ajust * opt.x[1]]

                                # Validar que todo esté bien.
                                valid = abs((estad.gamma.cdf(líms_dens[1], a=tp_paráms[0], loc=tp_paráms[1],
                                                             scale=tp_paráms[2]) -
                                             estad.gamma.cdf(líms_dens[0], a=tp_paráms[0], loc=tp_paráms[1],
                                                             scale=tp_paráms[2])) -
                                            dens)

                                # Si el error en la densidad de la distribución TODAVÍA queda superior al límite
                                # acceptable...
                                if valid > límite_precisión:
                                    raise ValueError('Error en la optimización de la distribución especificada. '
                                                     'Esto es un error de programación, así que mejor se queje al '
                                                     'programador. ({})'.format(correo))

                                # Guardar la distribución de todo modo.
                                tipo_dist = 'Gamma'
                                paráms = {'a': tp_paráms[0], 'ubic': tp_paráms[1], 'escl': tp_paráms[2]}

                    else:
                        raise ValueError('Tikon no tiene funciones para especificar a priores discretos en un intervalo'
                                         '(R, inf). Si lo quieres contribuir, ¡dale pués!')

                else:  # El caso (R, R)
                    if cont:

                        # Una distribución normal truncada con límites especificados y mu en la mitad del rango
                        # especificado
                        mu = (líms_dens[0] + líms_dens[1]) / 2
                        opt = minimizar(
                            lambda x: abs((estad.truncnorm.cdf(líms_dens[1], a=(mín - mu) / x, b=(máx - mu) / x,
                                                               loc=mu, scale=x) -
                                           estad.truncnorm.cdf(líms_dens[0], a=(mín - mu) / x, b=(máx - mu) / x,
                                                               loc=mu, scale=x)) -
                                          dens),
                            # bounds=[(1e-10, None)],  # para hacer: activar este
                            x0=np.array([líms_dens[1] - líms_dens[0]]),
                            method='Nelder-Mead')

                        tp_paráms = np.array([mu, opt.x[0], (mín - mu) / opt.x[0], (máx - mu) / opt.x[0]])

                        # Validar la optimización
                        valid = abs((estad.truncnorm.cdf(líms_dens[1], loc=tp_paráms[0], scale=tp_paráms[1],
                                                         a=tp_paráms[2], b=tp_paráms[3]) -
                                     estad.truncnorm.cdf(líms_dens[0], loc=tp_paráms[0], scale=tp_paráms[1],
                                                         a=tp_paráms[2], b=tp_paráms[3], ))
                                    - dens)

                        # Si validó bien, guardar la distribución...
                        if valid < límite_precisión:
                            tipo_dist = 'NormalTrunc'
                            paráms = {'a': tp_paráms[2], 'b': tp_paráms[3], 'ubic': tp_paráms[0], 'escl': tp_paráms[1]}

                        else:
                            # ... si no, intentar con una distribución beta.
                            opt = minimizar(
                                lambda x: abs((estad.beta.cdf(líms_dens[1], a=x[0], b=x[1], loc=mín, scale=máx - mín) -
                                               estad.beta.cdf(líms_dens[0], a=x[0], b=x[1], loc=mín,
                                                              scale=máx - mín)) -
                                              dens), bounds=[(1e-10, None), (1e-10, None)],
                                x0=np.array([1e-10, 1e-10]))

                            tp_paráms = [opt.x[0], opt.x[1], mín, máx - mín]

                            valid = abs(
                                (estad.beta.cdf(líms_dens[1], a=tp_paráms[0], b=tp_paráms[1], loc=mín,
                                                scale=máx - mín) -
                                 estad.beta.cdf(líms_dens[0], a=tp_paráms[0], b=tp_paráms[1], loc=mín,
                                                scale=máx - mín)) -
                                dens)

                            # Avizar si todavía no optimizó bien
                            if valid > límite_precisión:
                                raise ValueError('Error en la optimización de la distribución especificada. Esto es un '
                                                 'error de programación, así que mejor se queje al '
                                                 'programador. ({})'.format(correo))

                            tipo_dist = 'Beta'
                            paráms = {'a': tp_paráms[0], 'b': tp_paráms[1], 'ubic': tp_paráms[2], 'escl': tp_paráms[3]}

                    else:
                        raise ValueError('Tikon no tiene funciones para especificar a priores discretos en un intervalo'
                                         '(R, inf). Si lo quieres añadir, ¡dale pués!')

        # Inversar la distribución si necesario
        if inv:
            paráms['scale'] = -paráms['scale']

        return cls(tipo_dist=tipo_dist, paráms=paráms)

    @classmethod
    def _ajust_dist(cls, datos, líms, cont, lista_dist, nombre=None):
        return cls.aprox_dist(datos=datos, líms=líms, cont=cont)

    @classmethod
    def aprox_dist(cls, datos, líms, cont, lista_dist=None):
        """

        :param datos:
        :type datos:
        :param líms:
        :type líms:
        :param cont:
        :type cont:
        :param lista_dist:
        :type lista_dist:
        :return:
        :rtype: dict[str, VarSciPy | str | float | dict]
        """

        # Separar el mínimo y el máximo de la distribución
        mín_parám, máx_parám = líms

        # Un diccionario para guardar el mejor ajuste
        mejor_ajuste = dict(prms={}, tipo='', p=0.0)

        # Sacar las distribuciones del buen tipo (contínuas o discretas)
        if cont:
            categ_dist = 'cont'
        else:
            categ_dist = 'discr'

        dists_potenciales = [x for x in Ds.dists if Ds.dists[x]['tipo'] == categ_dist]

        if lista_dist is not None:
            dists_potenciales = [x for x in dists_potenciales if x in lista_dist]

        dists_potenciales = [x for x in dists_potenciales if x in cls.dists_disp()]

        # Verificar que todavia queden distribuciones para considerar.
        if len(dists_potenciales) == 0:
            raise ValueError('Ninguna de las distribuciones especificadas es apropiada para el tipo de distribución.')

        # Para cada distribución potencial para representar a nuestros datos...
        for nombre_dist in dists_potenciales:

            # El diccionario de la distribución
            dic_dist = Ds.dists[nombre_dist]

            # El máximo y el mínimo de la distribución
            mín_dist, máx_dist = dic_dist['límites']

            # Verificar que los límites del parámetro y de la distribución sean compatibles
            lím_igual = (((mín_dist == mín_parám == -np.inf) or
                          (not np.isinf(mín_dist) and not np.isinf(mín_parám))) and
                         ((máx_dist == máx_parám == np.inf) or
                          (not np.isinf(máx_dist) and not np.isinf(máx_parám))))

            # Si son compatibles...
            if lím_igual:

                if mín_parám == -np.inf and máx_parám != np.inf:
                    inv = True
                else:
                    inv = False

                # Restringimos las posibilidades para las distribuciones a ajustar, si necesario
                if np.isinf(mín_parám):

                    if np.isinf(máx_parám):
                        # Para el caso de un parámetro sín límites teoréticos (-inf, inf), no hay restricciones en la
                        # distribución.
                        restric = {}

                    else:
                        raise ValueError('No debería ser posible llegar hasta este error.')
                else:

                    if np.isinf(máx_parám):
                        # En el caso [R, inf), limitamos el valor inferior de la distribución al límite inferior del
                        # parámetro
                        restric = {'floc': mín_parám}

                    else:
                        # En el caso [R, R], limitamos los valores inferiores y superiores de la distribución.
                        if nombre_dist == 'Uniforme' or nombre_dist == 'Beta':
                            restric = {'floc': mín_parám, 'fscale': máx_parám - mín_parám}
                        elif nombre_dist == 'NormalTrunc':
                            restric = {'floc': (máx_parám + mín_parám) / 2}
                        elif nombre_dist == 'VonMises':
                            restric = {'floc': mín_parám + mat.pi, 'fscale': máx_parám - mín_parám}
                        else:
                            raise ValueError(nombre_dist)

                # Ajustar los parámetros de la distribución SciPy para caber con los datos.
                if nombre_dist == 'Uniforme':
                    # Para distribuciones uniformes, no hay nada que calibrar.
                    prms = {'ubic': restric['floc'], 'escl': restric['fscale']}
                else:
                    try:
                        tupla_prms = dic_dist['scipy'].fit(datos, **restric)
                        l_prms = dic_dist['paráms']
                        prms = {p: v for p, v in zip(l_prms, tupla_prms)}
                    except:
                        prms = None

                if prms is not None:
                    # Medir el ajuste de la distribución
                    prms_scipy = prms.copy()
                    prms_scipy['loc'] = prms_scipy.pop('ubic')
                    prms_scipy['scale'] = prms_scipy.pop('escl')
                    p = estad.kstest(rvs=datos, cdf=dic_dist['scipy'](**prms_scipy).cdf)[1]

                    # Si el ajuste es mejor que el mejor ajuste anterior...
                    if p > mejor_ajuste['p'] or mejor_ajuste['tipo'] == '':
                        # Guardarlo
                        mejor_ajuste['p'] = p
                        mejor_ajuste['prms'] = prms
                        mejor_ajuste['tipo'] = nombre_dist

                        # Inversar la distribución sinecesario
                        if inv and 'escl' in prms:
                            prms['escl'] = -prms['escl']

        # Si no logramos un buen aujste, avisar al usuario.
        if mejor_ajuste['p'] <= 0.10:
            avisar('El ajuste de la mejor distribución quedó muy mal (p = %f).' % round(mejor_ajuste['p'], 4))

        # Devolver la distribución con el mejor ajuste, tanto como el valor de su ajuste.
        resultado = {'dist': VarSciPy(tipo_dist=mejor_ajuste['tipo'], paráms=mejor_ajuste['prms']),
                     'nombre': mejor_ajuste['tipo'],
                     'prms': mejor_ajuste['prms'],
                     'p': mejor_ajuste['p']}

        return resultado

    @classmethod
    def de_líms(cls, líms, cont, nombre=None):
        """
        Esta función toma una "tupla" de límites para un parámetro de una función y devuelve una distribución
        Scipy correspondiente. Se usa en la inicialización de las
        distribuciones de los parámetros de ecuaciones.

        :param líms: Los límites para los valores posibles del parámetro. Para límites infinitas, usar np.inf y
        -np.inf. Ejemplos: (0, np.inf), (-10, 10), (-np.inf, np.inf).
        :type líms: tuple

        :param cont: Determina si el variable es continuo o discreto
        :type cont: bool

        :param nombre: Nombre para algunos tipos de distribuciones. Inútil para SciPy.
        :type nombre: str

        :return: Destribución no informativa conforme a las límites especificadas.
        :rtype: str
        """

        tipo_dist, paráms = _líms_a_dist(líms, cont)

        return cls(tipo_dist=tipo_dist, paráms=paráms)

    @staticmethod
    def dists_disp():
        return [x for x, d in Ds.dists.items() if d['scipy'] is not None]


class VarCalib(VarAlea):

    def __init__(símismo, nombre, tipo_dist, paráms):
        """

        :param nombre:
        :type nombre: str
        :param tipo_dist: El tipo de distribución. (P.ej., ``Normal``, ``Uniforme``, etc.)
        :type tipo_dist: str
        :param paráms:
        :type paráms: dict
        """

        super().__init__(tipo_dist=tipo_dist, nombre=nombre, paráms=paráms)

        símismo.var = NotImplemented

    def obt_var_base(símismo):
        """

        :return:
        :rtype: list | pm2.Stochastic | pm3.model.FreeRV
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

    @classmethod
    def de_densidad(cls, dens, líms_dens, líms, cont, nombre=None):
        raise NotImplementedError

    @classmethod
    def _ajust_dist(cls, datos, líms, cont, lista_dist, nombre=None):
        raise NotImplementedError

    @classmethod
    def de_líms(cls, líms, cont, nombre):
        raise NotImplementedError

    @staticmethod
    def dists_disp():
        raise NotImplementedError

    def __float__(símismo):
        """

        :return:
        :rtype: float
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
        :param tipo_dist:
        :type tipo_dist: str
        :param paráms:
        :type paráms: dict
        """

        super().__init__(nombre=nombre, tipo_dist=tipo_dist, paráms=paráms)

        # Sacar los límites y también verificar que existe este variable
        if tipo_dist in Ds.dists:
            líms_dist = Ds.dists[tipo_dist]['límites']
        elif tipo_dist in ['NormalExp', 'LogitInv']:
            líms_dist = (-np.inf, np.inf)
        else:
            raise ValueError('La distribución %s no existe en la base de datos de Tikon para distribuciones PyMC2.' %
                             tipo_dist)

        # Hacer transformaciones de forma de distribución si necesario

        # El caso (-inf, R] se transforma a [-R, inf)
        if líms_dist[0] == -np.inf and líms_dist[1] != np.inf:
            líms_dist[0] = -líms_dist[1]
            líms_dist[1] = np.inf
            inv = True  # Invertimos la distribución
            nombre = 'inv_{}'.format(nombre)
        else:
            inv = False

        # Transformar distribuciones con límites a distribuciones aproximativas con límites.
        if líms_dist[0] != -np.inf:
            if líms_dist[1] != np.inf:

                # El caso [R, R] se transforma con logit.
                avisar('A PyMC2 no le gustan distribuciones sin límites, como "{}". Tomaremos el logit inverso '
                       'de una distribución normal en vez.'.format(tipo_dist))

                # Normalizar la distribución inicial al rango [0, 1]
                d_scipy = VarSciPy(tipo_dist=tipo_dist, paráms=paráms)
                norm_suma = - (líms_dist[0] * paráms['escl'] + paráms['ubic'])
                norm_mult = 1 / (paráms['escl'] * (líms_dist[1] - líms_dist[0]))

                # Tomar la mitad de la densidad de esta distribución normalizada como el mu de nuestra distribución
                # normal
                mu = _logit((d_scipy.percentiles(0.5) + norm_suma) * norm_mult)

                # Aproximar sigma según los percentiles de la distribución original que corresponden a 1 desviación
                # estándar de la distribución normal.
                p16 = d_scipy.percentiles(estad.norm.cdf(-1))
                p84 = d_scipy.percentiles(estad.norm.cdf(1))
                sigma = (-_logit((p16 + norm_suma) * norm_mult) + _logit((p84 + norm_suma) * norm_mult)) / 2

                # Establecer la distribución Logit Inversa y sus parámetros
                paráms = {'mu': mu, 'sigma': sigma, 'escl': 1 / norm_mult, 'ubic': -norm_suma}
                tipo_dist = 'LogitInv'

            else:

                # El caso [R, inf) se transforma con log.
                avisar('A PyMC2 no le gustan distribuciones sin límites, como "{}". Tomaremos el exponencial '
                       'de una distribución normal en vez.'.format(tipo_dist))

                # Normalizar la distribución inicial para tener 99.9% se su densidad en el rango [0, 1]
                d_scipy = VarSciPy(tipo_dist=tipo_dist, paráms=paráms)
                norm_suma = - (líms_dist[0] * paráms['escl'] + paráms['ubic'])
                norm_mult = 1 / (paráms['escl'] * (d_scipy.percentiles(0.999) - líms_dist[0]))

                # Tomar la mitad de la densidad de esta distribución normalizada como el mu de nuestra distribución
                # normal
                mu = mat.log((d_scipy.percentiles(0.5) + norm_suma) * norm_mult)

                # Aproximar sigma según los percentiles de la distribución original que corresponden a 1 desviación
                # estándar de la distribución normal.
                p16 = d_scipy.percentiles(estad.norm.cdf(-1))
                p84 = d_scipy.percentiles(estad.norm.cdf(1))
                sigma = (-mat.log((p16 + norm_suma) * norm_mult) + mat.log((p84 + norm_suma) * norm_mult)) / 2

                # Establecer la distribución Normal Exponencial y sus parámetros
                if inv:
                    # De-invertir la distribución, si necesario.
                    paráms = {'mu': mu, 'sigma': sigma, 'escl': -1 / norm_mult, 'ubic': norm_suma}
                else:
                    paráms = {'mu': mu, 'sigma': sigma, 'escl': 1 / norm_mult, 'ubic': -norm_suma}

                tipo_dist = 'NormalExp'

        # Generar la distribución y sus parámetros
        dist = None
        if tipo_dist == 'NormalExp':
            var_base = pm2.Normal(nombre, mu=0, tau=1)
            var_base.keep_trace = False
            dist_transf = var_base * paráms['sigma'] + paráms['mu']
            nombre = 'NormalExp_{}'.format(nombre)
            dist = pm2.Lambda(nombre, lambda x=dist_transf: np.exp(x))
            dist.keep_trace = True

        elif tipo_dist == 'LogitInv':
            var_base = pm2.Normal(nombre, mu=0, tau=1)
            var_base.keep_trace = False
            dist_transf = var_base * paráms['sigma'] + paráms['mu']
            nombre = 'LogitInv_{}'.format(nombre)
            dist = pm2.InvLogit(nombre, dist_transf)
            dist.keep_trace = True

        elif tipo_dist == 'Cauchy':
            var_base = pm2.Cauchy(nombre, alpha=0, beta=1)

        elif tipo_dist == 'Laplace':
            var_base = pm2.Laplace(nombre, mu=0, tau=1)

        elif tipo_dist == 'Logística':
            var_base = pm2.Logistic(nombre, mu=0, tau=1)

        elif tipo_dist == 'Normal':
            var_base = pm2.Normal(nombre, mu=0, tau=1)

        elif tipo_dist == 'T':
            var_base = pm2.T(nombre, nu=paráms['df'])

        else:
            raise ValueError('La distribución "{}" existe en la base de datos de Tiko\'n para distribuciones PyMC2,'
                             'pero no está configurada en la clase VarPyMC2.'.format(tipo_dist))

        # Hacer transformaciones necesarias
        if dist is None:
            dist = var_base

        símismo.mult = paráms['escl']
        símismo.suma = paráms['ubic']

        símismo.var = dist
        símismo.var_base = var_base
        símismo.vars_mod = {dist, var_base}

        símismo.tipo_dist = tipo_dist

    def obt_var_base(símismo):

        return símismo.var_base

    def dibujar(símismo, ejes):

        n = 10000
        if símismo.var == símismo.var_base:
            puntos = np.array([símismo.var.rand() for _ in range(n)])
        else:
            dist_stoc = símismo.var_base
            puntos = np.array([(dist_stoc.rand(), símismo.var.value)[1] for _ in range(n)])

        # Transformaciones necesarias
        puntos = np.add(np.multiply(puntos, símismo.mult), símismo.suma)

        # Crear el histograma
        y, delim = np.histogram(puntos, normed=True, bins=n // 100)
        x = 0.5 * (delim[1:] + delim[:-1])

        # Dibujar el histograma
        ejes[0].plot(x, y, 'b-', lw=2, alpha=0.6)
        ejes[0].set_title('Distribución')

        # Dibujar la traza sí misma
        ejes[1].plot(símismo.traza())
        ejes[1].set_title('Traza')

    def traza(símismo):
        """
        Devuelve la traza del variable. Si no hay traza, devuelve un matriz vacía.

        :return: La traza del variable.
        :rtype: np.ndarray
        """

        # Devolver la traza si existe.
        try:
            # Intentar obtener la traza.
            trz = símismo.var.trace(chain=None)[:]

            # Devolver la traza con las transformaciones necesaria.
            return np.add(np.multiply(trz, símismo.mult), símismo.suma)

        except (AttributeError, TypeError):
            # Si hubo error, devolver una matriz vacía.
            return np.array([])

    @classmethod
    def de_densidad(cls, dens, líms_dens, líms, cont, nombre=None):
        """
        Devuelve un objeto de variable PyMC2 a base de información de distribución de densidad y de límites teoréticos.

        :param dens: La fracción (en ``[0, 1]``) de densidad que caye adentro de ``líms_prcnt``. 
        :type dens: float | int

        :param líms_dens: Los límites adentro de cuales ``frac`` densidad cae.
        :type líms_dens: np.ndarray | list | tuple

        :param líms: Los límites teoréticos del variable.
        :type líms: np.ndarray | list | tuple

        :param cont: Si es una distribución continua o no.
        :type cont: bool

        :param nombre: El nombre del variable.
        :type nombre: str

        :return: El variable PyMC2.
        :rtype: VarPyMC2

        """

        # Convertir None a infinidad en los límites de densidad y teoréticos.
        mín = líms[0] if líms[0] is not None else -np.inf
        máx = líms[1] if líms[1] is not None else np.inf

        rango = np.array([líms_dens[0] if líms_dens[0] is not None else -np.inf,
                          líms_dens[1] if líms_dens[1] is not None else np.inf])  # Los límites de densidad

        # Validar los rangos y límites
        if rango[0] < mín or rango[1] > máx:
            raise ValueError('Los límites de densidad ({}, {}) están afuera del rango teorético ({}, {}).'
                             .format(rango[0], rango[1], mín, máx))

        # Inicializar el diccionario de parámetros.
        paráms = {'escl': 1, 'ubic': 0}

        # Primero, arreglar unos casos especiales que nos podrían causar problemas después...

        # Si tenemos una densidad de 100% en el rango especificado...
        if dens == 1:
            # Generar la distribución con este rango en vez.
            return cls.de_líms(líms=rango, cont=cont, nombre=nombre)

        # No se puede tener límites de densidad iguales con densidad < 1, por supuesto.
        if líms_dens[0] == líms_dens[1]:
            raise ValueError('No se puede tener una densidad < 1 en un rango [a, b] si a = b.')

        # Si los rangos de la densidad corresponden con los rangos teoréticos, pero con densidad < 1...
        if rango[0] == mín and rango[1] == máx:
            raise ValueError('No se puede tener una densidad < 1 en un rango igual al rango teorético.')

        # Invertir distribuciones entre (-inf, R]
        if mín == -np.inf and máx != np.inf:
            mín = -máx
            máx = np.inf
            paráms['escl'] = -1

        # Ahora, crear la distribución apriopiada.
        if mín == -np.inf:
            if máx == np.inf:
                # El caso (-inf, inf). Muy facil.

                # Calcular los parámetros de una distribución normal.
                mu = np.mean(rango)  # El promedio del rango de densidad
                # Calcular sigma analíticamente
                sigma = ((rango[1] - rango[0]) / 2) / estad.norm.ppf((1 - dens) / 2 + dens)

                # Especificar la distribución.
                tipo_dist = 'Normal'
                paráms = {'ubic': mu, 'escl': sigma}

            else:
                # Ya convertimos distribuciones en (-inf, R] a [-R, inf), así que no debería ser posible llegar
                # hasta este error.
                raise ValueError('No debería ser posible llegar hasta este error.')

        else:

            # Primero, normalizar el límite inferior.
            paráms['ubic'] += mín
            rango = np.subtract(rango, mín)
            máx -= mín

            if máx == np.inf:
                # El caso [R, inf)

                if rango[0] == 0:
                    # Si el límite inferior del rango de densidad es igual al límite teorético, solamente tenemos
                    # que asegurarnos que ``dens`` densidad quede abajo del límite inferior transformado.

                    lím_norm_sup = np.log(rango[1])  # El límite superior de densidad en la distribución normal

                    sigma = 1  # Tomar un sigma de 1, por simplicidad. De verdad no importa mucho.
                    mu = lím_norm_sup - estad.norm(0, 1).ppf(dens)  # Mu en función de sigma y la densidad

                else:
                    # Sino, tenemos que asegurarnos que la densidad caiga entre los dos límites transformados.
                    log_rango = np.log(rango)

                    mu = np.mean(log_rango)  # Mu es el promedio entre ambos límites de densidad

                    # Sigma se calcular analíticamente
                    sigma = ((log_rango[1] - log_rango[0]) / 2) / estad.norm.ppf((1 - dens) / 2 + dens)

                # Especificar la distribución Normal Exponencial
                tipo_dist = 'NormalExp'
                paráms['mu'] = mu
                paráms['sigma'] = sigma

            else:
                # El caso [R, R]

                # Normalizar la distribución
                paráms['escl'] *= máx
                rango = np.divide(rango, máx)

                if rango[0] == 0:
                    # Si el límite inferior del rango de densidad es igual al límite teorético, solamente tenemos
                    # que asegurarnos que ``dens`` densidad quede abajo del límite superior transformado.
                    lím_norm_sup = _logit(rango[1])

                    sigma = 1  # Tomar un sigma de 1, por simplicidad. De verdad no importa mucho.
                    mu = lím_norm_sup - estad.norm(0, 1).ppf(dens)  # Mu en función de sigma y la densidad

                elif rango[1] == 1:
                    # Si el límite superior del rango de densidad es igual al límite teorético, solamente tenemos
                    # que asegurarnos que la densidad quede arriba del límite inferior transformado.
                    lím_norm_inf = _logit(rango[0])

                    sigma = 1  # Tomar un sigma de 1, por simplicidad. De verdad no importa mucho.
                    mu = lím_norm_inf - estad.norm(0, 1).ppf(1 - dens)  # Mu en función de sigma y la densidad

                else:
                    # Sino, tenemos que asegurarnos que la densidad caiga entre los dos límites transformados.
                    lgt_rango = np.log(np.divide(rango, np.subtract(1, rango)))

                    mu = np.mean(lgt_rango)  # Mu es el promedio entre ambos límites de densidad

                    # Sigma se calcular analíticamente
                    sigma = ((lgt_rango[1] - lgt_rango[0]) / 2) / estad.norm.ppf((1 - dens) / 2 + dens)

                # Especificar la distribución Logit Inverso
                tipo_dist = 'LogitInv'
                paráms['mu'] = mu
                paráms['sigma'] = sigma

        return cls(nombre=nombre, tipo_dist=tipo_dist, paráms=paráms)

    @classmethod
    def _ajust_dist(cls, datos, líms, cont, lista_dist, nombre=None):
        """

        :param datos:
        :type datos:
        :param líms:
        :type líms:
        :param cont:
        :type cont:
        :param lista_dist: La lsita de distribuciones posibles. Si no se especifica, se tomará la lista de
          distribuciones disponibles para este tipo de variable. El uso de límites (-inf, +inf) en las llamadas a
          :func:`VarSciPy.aprox_dist` aseguran que éste únicamente tome distribuciones sin límites.
        :type lista_dist: list[str]
        :param nombre:
        :type nombre:
        :return:
        :rtype:
        """

        mín = líms[0] if líms[0] is not None else -np.inf
        máx = líms[1] if líms[1] is not None else np.inf

        transf = {'mult': 1, 'suma': 0}
        if mín == -np.inf and máx != np.inf:
            mín = -máx
            máx = np.inf
            transf['mult'] = -1

        if mín == -np.inf:
            if máx == np.inf:
                ajustado = VarSciPy.aprox_dist(datos=datos, líms=(-np.inf, np.inf), cont=cont, lista_dist=lista_dist)
                tipo_dist = ajustado['nombre']
                paráms = ajustado['prms']  # Sacar el los parámetros de la distribución

            else:
                raise ValueError('No debería ser posible llegar hasta este error.')
        else:
            # Normalizar el límite inferior.
            transf['suma'] += mín
            máx -= mín
            datos = np.subtract(datos, mín)  # No borrar datos originales

            # Evitar log(0) y logit(0)
            if np.min(datos) == 0:
                transf['suma'] -= 1e-5
                máx += 1e-5
                datos = np.add(datos, 1e-5)

            if máx == np.inf:

                log_datos = np.log(datos)
                ajustado = VarSciPy.aprox_dist(datos=log_datos, líms=(-np.inf, np.inf),
                                               cont=cont, lista_dist=['Normal'])
                tipo_dist = 'NormalExp'
                paráms = {'mu': ajustado['prms']['ubic'], 'sigma': ajustado['prms']['escl'],
                          'ubic': transf['suma'], 'escl': transf['mult']}

            else:
                transf['mult'] *= máx
                datos = np.divide(datos, máx)  # No borrar datos originales

                # Evitar logit(1)
                if np.max(datos) == 1:
                    transf['mult'] /= (1 - 1e-5)
                    datos = np.multiply(datos, 1 - 1e-5)

                lgt_datos = _logit(datos)

                ajustado = VarSciPy.aprox_dist(datos=lgt_datos, líms=(-np.inf, np.inf), cont=cont,
                                               lista_dist=['Normal'])
                tipo_dist = 'LogitInv'
                paráms = {'mu': ajustado['prms']['ubic'], 'sigma': ajustado['prms']['escl'],
                          'ubic': transf['suma'], 'escl': transf['mult']}

        return {'dist': cls(nombre=nombre, tipo_dist=tipo_dist, paráms=paráms), 'p': ajustado['p']}

    @classmethod
    def de_líms(cls, líms, cont, nombre):

        tipo_dist, paráms = _líms_a_dist(líms=líms, cont=cont)

        return cls(nombre=nombre, tipo_dist=tipo_dist, paráms=paráms)

    @staticmethod
    def dists_disp():
        return ['Beta', 'Cauchy', 'Chi2', 'Exponencial', 'WeibullExponencial', 'Gamma', 'MitadCauchy', 'MitadNormal',
                'GammaInversa', 'Laplace', 'Logística', 'LogNormal', 'Normal', 'Pareto', 'T',
                'NormalTrunc', 'Uniforme', 'VonMises', 'Weibull', 'Bernoulli', 'Binomial', 'Geométrica',
                'Hypergeométrica', 'BinomialNegativo', 'Poisson', 'UnifDiscr',
                'NormalExp', 'LogitInv'  # Funciones auxiliares para transformaciones
                ]

    def __float__(símismo):
        return float(símismo.var.value) * símismo.mult + símismo.suma


class VarPyMC3(VarCalib):
    """
    Esta clase representa variables de PyMC v3.
    """

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
            dist = pm3.StudentT(nombre=nombre, nu=paráms['df'], mu=paráms['loc'],
                                sd=paráms['scale'])  # para hacer: verificar
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

    def obt_var_base(símismo):
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

    @classmethod
    def de_densidad(cls, dens, líms_dens, líms, cont, nombre=None):
        raise NotImplementedError

    @classmethod
    def _ajust_dist(cls, datos, líms, cont, lista_dist, nombre=None):
        raise NotImplementedError

    @classmethod
    def de_líms(cls, líms, cont, nombre):
        raise NotImplementedError

    @staticmethod
    def dists_disp():

        return ['Beta', 'Cauchy', 'Chi2', 'Exponencial', 'Gamma', 'MitadCauchy', 'MitadNormal', 'GammaInversa',
                'Laplace', 'Logística', 'LogNormal', 'Normal', 'Pareto', 'T', 'NormalTrunc', 'Uniforme', 'VonMises',
                'Weibull', 'Bernoulli', 'Binomial', 'Geométrica', 'BinomialNegativo', 'Poisson', 'UnifDiscr']

    def __float__(símismo):
        raise NotImplementedError('')


# Funciones auxiliares
def _líms_a_dist(líms, cont):
    # Sacar el mínimo y máximo de los límites.
    mín = líms[0] if líms[0] is not None else -np.inf
    máx = líms[1] if líms[1] is not None else np.inf

    # Verificar que máx > mín
    if máx <= mín:
        raise ValueError('El valor máximo debe ser superior al valor máximo.')

    # Pasar a través de todos los casos posibles
    if mín == -np.inf:
        if máx == np.inf:  # El caso (-np.inf, np.inf)
            if cont:
                tipo_dist = 'Normal'
                paráms = {'ubic': 0, 'escl': 1e10}
            else:
                tipo_dist = 'UnifDiscr'
                paráms = {'ubic': 1e-10, 'escl': 1e10}

        else:  # El caso (-np.inf, R)
            if cont:
                tipo_dist = 'Exponencial'
                paráms = {'ubic': -máx, 'escl': -1e10}
            else:
                tipo_dist = 'Geométrica'
                paráms = {'k': 1e-8, 'ubic': -máx}

    else:
        if máx == np.inf:  # El caso (R, np.inf)
            if cont:
                tipo_dist = 'Exponencial'
                paráms = {'ubic': mín, 'escl': 1e10}
            else:
                ubic = mín - 1  # Para incluir mín en los valores posibles de la distribución.
                tipo_dist = 'Geométrica'
                paráms = {'p': 1e-8, 'ubic': ubic}

        else:  # El caso (R, R)
            if cont:
                escl = máx - mín
                tipo_dist = 'Uniforme'
                paráms = {'ubic': mín, 'escl': escl}
            else:
                tipo_dist = 'UnifDiscr'
                paráms = {'low': mín, 'high': mín + 1}

    return tipo_dist, paráms


def _logit(x):
    return np.log(x / (1 - x))


def _inv_logit(x):
    return np.divide(np.exp(x), np.add(np.exp(x), 1))
