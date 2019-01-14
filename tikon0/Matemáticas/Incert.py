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
        # que ecs, del número de repeticiones para cada calibración.
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
