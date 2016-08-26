import random as aleatorio

import numpy as np

from COSO import Simulable
from Matemáticas.CALIB import extraer_objetos, leerdatos


# Este módulo maneja el análisis de incertidumbre de los modelos.


def anal_incert(objeto, opciones_simul, conf=0.95, rep=None, tiempo_inic=None, tiempo_fin=None, datos=None):
    if not isinstance(objeto, Simulable):
        raise TypeError('anal_incert requiere un objeto de tipo "Simulable".')

    simul = objeto.simul

    # Calcular los tiempos iniciales y finales
    if datos is None:
        if hasattr(objeto, 'datos') and objeto.datos is not None:
            datos = objeto.datos
            lista_obs, matriz_tiempos = leerdatos(datos)
            if tiempo_fin is None:
                tiempo_fin = [t.max() for t in matriz_tiempos]
            if tiempo_inic is None:
                tiempo_inic = [t.min() for t in matriz_tiempos]
        else:
            datos = {}
            if tiempo_fin is None or tiempo_inic is None:
                return 'Se necesita ingresar fechas para el análisis de incertidumbre.'

    if type(tiempo_fin) is int or type(tiempo_fin) is float:
        tiempo_fin = [tiempo_fin] * min(1, len(datos))
    if type(tiempo_inic) is int or type(tiempo_inic) is float:
        tiempo_inic = [tiempo_inic] * min(1, len(datos))

    lista_objetos = extraer_objetos(objeto)
    lista_objetos = [x for x in lista_objetos if 'coefs' in x.dic]

    núm_total = núm_en_inter = 0
    lista_res_alea = []
    for n_exp, exp in enumerate(sorted(datos.keys())):
        print(objeto.objetos['insectos']['araña'].fases['Adulto'].pob)
        print(objeto.objetos['insectos']['mosca'].fases['Adulto'].pob)

        # Poner parámetros a valores aleatorios
        resultados_alea = []
        n_iter = []
        # Calcular el número de iteraciones en cada dic_incert
        for n, obj in enumerate(lista_objetos):
            n_iter.append(len(obj.dic_incert[list(obj.dic_incert.keys())[0]]))
        if max(n_iter) != min(n_iter):
            print('Aviso: no todos los objetos del análisis de incertidumbre tienen el mismo número de iteraciones.'
                  'Las distribuciones de sus parámetros se considerarán como distribuciones independientes.')
        # Si se pidieron más repeticiones que haya iteraciones en dic_incert,
        # tomar el número de iteraciones disponibles
        if rep is None:
            rep = max(n_iter)
        rep = min(rep, max(n_iter))
        l_rep = []
        for n, i in enumerate(n_iter):
            l_rep.append(min(rep, i))

        aleatorios = aleatorio.sample(range(max(n_iter)), rep)
        for i in aleatorios:
            for obj in lista_objetos:
                escoger_parám(obj.dic['coefs'], obj.dic_incert, n=i)
            resultados_alea.append(simul(tiempo_inic=tiempo_inic[n_exp],
                                         tiempo_final=tiempo_fin[n_exp], **opciones_simul))

        # Cambiar el formato de los resultados para que cada valor del variable sea una matriz numpy 2D con una línea
        # de la matriz para cada corrida.
        resultados_alea = arreglar_resultados(resultados_alea)
        lista_res_alea.append(resultados_alea)

        # Calcular los límites de los intervales de confianza
        resultados_mín, resultados_máx = calc_intervalos(resultados_alea, conf)

        # Calcular el % de los datos que caen en el interval de confianza
        result_interv = validar_intervalo(datos[exp], resultados_mín, resultados_máx)
        núm_en_inter += result_interv[0]
        núm_total += result_interv[1]

    # Devolver el % de los datos que caen en el interval de confianza y los resultados de las corridas
    return núm_en_inter/núm_total, lista_res_alea


def escoger_parám(d, d_i, n):
    """

    :param d: diccionario de un objeto
    :param d_i: diccionario de incertidumbre del mismo objeto
    :param n: el índice del punto en las cadenas de d_i a implementar en d
    :return: nada
    """

    if type(d) is dict:
        i = [x for x in sorted(d.items())]
    elif type(d) is list:
        i = enumerate(d)
    else:
        raise ValueError('escribir_dic_incert() necesita una lista o diccionario como parámetro.')

    for ll, v in i:  # Para cada llave y valor del diccionario...
        if type(v) is dict or type(v) is list:  # Si el valor de la llave es otro diccionario:
            escoger_parám(v, d_i[ll], n)  # Repetir la funcción con el nuevo diccionario
        elif isinstance(v, int) or isinstance(v, float):  # Sólamente incluir los parámetros numéricos
            n %= len(d_i[ll])  # Si n > el número de iteraciones en la cadena, reempezamos del principio
            d[ll] = d_i[ll][n]
        else:
            raise ValueError('Valor no numérico en el diccionario.')


# Dos funciones obscuras para poner el formato requísito a los resultados de las corridas de análisis de incertidumbre.
# Empezando con formato de una lista de corridas:
# [{var1: [1, 2, 3], var2: [4, 5, 6]}, {var1: [7, 8, 9], var2: [10, 11, 12]}],
# da el formato:
# {var1: [[1, 2, 3], [7, 8, 9]], var2: [[4, 5, 6], [10, 11, 12]]}
# (Todas las listas las regresa como matrices numpy.)

def arreglar_resultados(resultados):
    arreglados = None
    for corrida in resultados:
        if arreglados is None:
            arreglados = corrida.copy()
        else:
            arreglados = arreglar(corrida, arreglados)

    return arreglados


def arreglar(c, a):
    for ll, v in c.items():
        if type(v) is dict:
            arreglar(v, a=a[ll])
        elif type(v) is np.ndarray or type(v) is list:
            a[ll] = np.vstack((a[ll], c[ll]))

    return a


# Para calcular intervalos de confianza
def calc_intervalos(r, conf, r_mín=None, r_máx=None):
    """

    :param r:
    :param conf:
    :param r_mín:
    :param r_máx:
    :return:
    """
    if r_mín is None:
        r_mín = {}
    if r_máx is None:
        r_máx = {}

    for ll, v in r.items():
        if type(v) is dict:
            r_mín[ll] = {}
            r_máx[ll] = {}
            calc_intervalos(v, conf, r_mín[ll], r_máx[ll])
        elif type(v) is np.ndarray or type(v) is list:
            r_mín[ll] = np.percentile(r[ll], (1 - conf) / 2, axis=0)
            r_máx[ll] = np.percentile(r[ll], 1/2 + conf/2, axis=0)

    return r_mín, r_máx


def validar_intervalo(d, r_mín, r_máx, en_in=0, t=0):
    """
    Valida el intervalo de confianza
    :param d: diccionario de datos
    :param r_mín: diccionario del mínimo de cada variable en d según el intervalo de confianza
    :param r_máx: diccionario del máximo de cada variable en d según el intervalo de confianza
    :param t:
    :param en_in:
    :return: conteo ('tuple')
    """

    for ll, v in d.items():
        if type(v) is dict:
            en_in, t = validar_intervalo(v, r_mín[ll], r_máx[ll], en_in=en_in, t=t)
        elif type(v) is tuple:
            v = v[1]  # Sacar los datos y quitar la lista de tiempo
            en_in += sum((r_mín[ll] < v) & (v < r_máx[ll]))  # Datos que caen en el intervalo
            t += len(v)  # Número total de datos

    return en_in, t