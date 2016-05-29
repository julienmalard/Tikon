import os
import warnings as avisar
import numpy as np
import matplotlib.pyplot as dib
import pymc

import INCERT.Distribuciones as Ds

"""
Este código contiene funciones para manejar datos de incertidumbre.
"""


def gen_vector_coefs(dic_parám, calibs, n_rep_parám, comunes=None):
    """
    Esta función genera una matríz de valores posibles para un coeficiente, dado los nombres de las calibraciones
      que queremos usar y el número de repeticiones que queremos.

    :param dic_parám: Un diccionario de un parámetro con todas sus calibraciones
    :type dic_parám: dict

    :param calibs: Cuáles calibraciones hay que incluir
    :type calibs: list

    :param n_rep_parám: El número de repeticiones paramétricas que queremos en nuestra simulación.
    :type n_rep_parám: int

    :param comunes: Una matriz con la ubicación de cuál dato tomar de cada traza, si queremos que haya correspondencia
      entre los datos elegidos de cada parámetro.
    :type comunes: np.ndarray

    :return: Una matriz unidimensional con los valores del parámetro.
    :rtype: np.ndarray

    """

    # Hacer una lista con únicamente las calibraciones que estén presentes y en la lista de calibraciones acceptables,
    # y en el diccionario del parámetro
    calibs_usables = [x for x in dic_parám if x in calibs]

    # La lista para guardar las partes de las trazas de cada calibración que queremos incluir en la traza final
    lista_trazas = []

    # El número de calibraciones en la lista de calibraciones usables
    n_calibs = len(calibs_usables)

    # Calcular el número de repeticiones paramétricas por calibración. Produce una lista, en el mismo orden que calibs,
    # del número de repeticiones para cada calibración.
    rep_per_calib = np.array([n_rep_parám // n_calibs] * n_calibs)

    # Calcular el número que repeticiones que no se dividieron igualmente entre las calibraciones...
    resto = n_rep_parám % n_calibs
    # ...y añadirlas la principio de la lista de calibraciones.
    rep_per_calib[:resto + 1] += 1

    # Para cada calibración en la lista...
    for n_id, id_calib in enumerate(calibs_usables):

        # Sacar su traza (o distribución) del diccionario del parámetro.
        traza = dic_parám[id_calib]

        # Si la traza es una matriz numpy...
        if type(traza) is np.ndarray:

            # Verificamos si necesitamos más repeticiones de esta traza que tiene de datos disponibles.
            if rep_per_calib[n_id] > len(dic_parám[id_calib]):

                # Si es el caso que la traza tiene menos datos que las repeticiones que queremos...
                avisar.warn('Número de replicaciones superior al tamaño de la traza de '
                            'parámetro disponible.')

                # Vamos a tener que repetir datos
                devolver = True

            else:
                # Si no, no hay pena
                devolver = False

            # Tomar, al hazar, datos de la traza. Si estamos usando calibraciones comunes para todos los parámetros,
            # usar la ubicación de los datos predeterminada.
            if comunes is not None:
                ubic_datos = comunes[:rep_per_calib[n_id]]
                nuevos_vals = traza[ubic_datos]
            else:
                nuevos_vals = np.random.choice(traza, size=rep_per_calib[n_id], replace=devolver)

        elif type(traza) is str:
            # Si la traza es en formato de texto...

            if comunes:
                avisar.warn('No se pudo guardar la correspondencia entre todas las calibraciones por presencia'
                            'de distribuciones SciPy. La correspondencia sí se guardo para las otras calibraciones.')

            # Convertir el texto a distribución de SciPy
            dist_sp = Ds.texto_a_distscipy(traza)

            # Sacar los datos necesarios de la distribución SciPy
            nuevos_vals = dist_sp.rvs(rep_per_calib[n_id])

        elif isinstance(traza, pymc.Stochastic):

            # Si es un variable de calibración activo, poner el variable sí mismo en la matriz
            nuevos_vals = traza

        else:
            raise ValueError

        # Añadir los datos de esta calibración a la lista de datos para la traza general.
        lista_trazas.append(nuevos_vals)

    # Combinar las trazas de cada calibración en una única matriz numpy unidimensional.
    return np.concatenate(lista_trazas)


def gráfico(matr_predic, vector_obs, nombre, etiq_y=None, etiq_x='Día', color=None, mostrar=True, archivo=''):
    """
    Esta función genera un gráfico, dato una matriz de predicciones y un vector de observaciones temporales.

    :param matr_predic: La matriz de predicciones. Eje 0 = incertidumbre estocástica, eje 1 = incertidumbre
      paramétrica, eje 2 = día.
    :type matr_predic: np.ndarray

    :param vector_obs: El vector de las observaciones. Eje 0 = tiempo.
    :type vector_obs: np.ndarray

    :param nombre: El título del gráfico
    :type nombre: str

    :param etiq_y: La etiqueta para el eje y del gráfico.
    :type etiq_y: str

    :param etiq_x: La etiqueta para el eje x del gráfico
    :type etiq_x: str

    :param color: El color para el gráfico
    :type color: str

    :param mostrar: Si hay que mostrar el gráfico de inmediato, o solo guardarlo.
    :type mostrar: bool

    :param archivo: El archivo donde guardar el gráfico
    :type archivo: str

    """

    assert len(vector_obs) == matr_predic.shape[2]

    if color is None:
        color = '#99CC00'

    if etiq_y is None:
        etiq_y = nombre

    if mostrar is False:
        if len(archivo) == 0:
            raise ValueError('Hay que especificar un archivo para guardar el gráfico de %s.' % nombre)

    prom_predic = matr_predic.mean(axis=(0, 1))

    x = np.arange(len(vector_obs))

    dib.plot(x, prom_predic, lw=2, color=color)

    dib.plot(x, vector_obs, 'o', color=color)

    # Una matriz sin la incertidumbre estocástica
    matr_prom_estoc = matr_predic.mean(axis=0)

    # Ahora, el eje 0 es el eje de incertidumbre paramétrica
    máx_parám = matr_prom_estoc.max(axis=0)
    mín_parám = matr_prom_estoc.min(axis=0)

    dib.fill_between(x, máx_parám, mín_parám, facecolor=color, alpha=0.5)

    máx_total = matr_predic.max(axis=(0, 1))
    mín_total = matr_predic.min(axis=(0, 1))

    dib.fill_between(x, máx_total, mín_total, facecolor=color, alpha=0.3)

    dib.xlabel(etiq_x)
    dib.ylabel(etiq_y)
    dib.title(nombre)

    if mostrar is True:
        dib.show()
    else:
        if '.png' not in archivo:
            archivo = os.path.join(archivo, nombre + '.png')
        dib.savefig(archivo)
