import numpy as np
import random as aleatorio

from INCERT.CALIB import leerdatos


# Este módulo maneja el análisis de incertidumbre de los modelos.


def anal_incert(objeto, conf=0.95, rep=100, tiempo_inic=None, tiempo_fin=None):
    dic = objeto.dic
    dic_incert = objeto.dic_incert
    modelo = objeto.simul
    if hasattr(objeto, 'datos'):
        datos = objeto.datos

    # Calcular los tiempos iniciales y finales
    if datos:
        lista_obs, lista_tiempos = leerdatos(datos)
        if tiempo_fin is None:
            tiempo_fin = max(lista_tiempos)
        if tiempo_inic is None:
            tiempo_inic = min(lista_tiempos)
    else:
        if tiempo_fin is None or tiempo_inic is None:
            return 'Se necesita ingresar fechas para el análisis de incertidumbre.'
    lista_parám = sacar_parám(dic_incert)

    # Poner parámetros a valores aleatorios
    res_alea = []
    n_iter = len(dic_incert[list(dic_incert.keys())[0]])  # El número de iteraciones en dic_incert.
    # Si se pidieron más repeticiones que haya iteraciones en dic_incert, tomar el número de iteraciones disponibles
    if rep > n_iter:
        print("Aviso: Sólo hay %s iteraciones disponibles para el análisis de incertidumbre." % n_iter)
        rep = n_iter
    aleatorios = aleatorio.sample(range(0, n_iter), rep)
    for i in aleatorios:
        paráms = []
        for j in range(len(lista_parám)):
            paráms.append(lista_parám[j][i])
        escribir_parám(dic, parámetros=paráms)
        res_alea.append(modelo(tiempo_final=tiempo_fin, tiempo_inic=tiempo_inic))

    # Cambiar el formato de los resultados para que cada valor del variable sea una matriz numpy 2D con una línea
    # de la matriz para cada corrida.
    res_alea = arreglar_resultados(res_alea)

    # Calcular los límites de los intervales de confianza
    resultados_mín, resultados_máx = calc_intervales(res_alea, conf)

    # Calcular el % de los datos que caen en el interval de confianza
    por_en_inter = validar_interval(datos, resultados_mín, resultados_máx)

    # Devolver el % de los datos que caen en el interval de confianza y los resultados de las corridas
    return por_en_inter, res_alea


def sacar_parám(d, l=None):
    if not l:
        l = []

    for ll, v in sorted(d.items()):
        if type(v) is dict:
            sacar_parám(v, l=l)
        elif type(v) is list:
            if type(v[0]) is float or type(v[0]) is int:
                l.append(v)
            elif type(v[0]) is list:
                sacar_parám(v, l=l)

    return l


def escribir_parám(d, parámetros, n=0):
    for ll, v in sorted(d.items()):  # Para cada llave (ordenada alfabéticamente) y valor del diccionario...
        if type(v) is dict:  # Si el valor de la llave es otro diccionario:
            escribir_parám(v, parámetros=parámetros, n=n)  # Repetir la funcción con el nuevo diccionario
        elif isinstance(v, int) or isinstance(v, float):  # Sólamente incluir los parámetros numéricos
            d[ll] = parámetros[n].value
            n += 1
        # Si la llave refiere a una lista de valores
        elif type(v) is list and (type(v[0]) is float or type(v[0]) is int):
            for j in v:
                d[ll][j] = parámetros[n].value
                n += 1


# Dos funciones obscuras para poner el formato requísito a los resultados de las corridas de análisis de incertidumbre.
# Empezando con formato {corrida1: {var1: [1, 2, 3], var2: [4, 5, 6]}, corrida2: {var1: [7, 8, 9], var2: [10, 11, 12]}},
# da el formato:
# {var1: [[1, 2, 3], [7, 8, 9]], var2: [[4, 5, 6], [10, 11, 12]]}
# (Todas las listas las regresa como matrices numpy.)
def arreglar_resultados(resultados):
    arreglados = None
    for corrida in resultados:
        if not arreglados:
            arreglados = resultados[corrida]
        else:
            arreglados = arreglar(resultados[corrida], arreglados)

    return arreglados


def arreglar(c, a):
    for ll, v in c.items():
        if type(v) is dict:
            arreglar(v, a=a[ll])
        elif type(v) is np.ndarray or type(v) is list:
            a[ll] = np.vstack((a[ll], c[ll]))

    return a


# Para calcular intervales de confianza
def calc_intervales(r, conf, r_mín=None, r_máx=None):
    if r_mín is None:
        r_mín = r.copy()
    if r_máx is None:
        r_máx = r.copy()
    for ll, v in r.items():
        if type(v) is dict:
            calc_intervales(v, conf, r_mín[ll], r_máx[ll])
        elif type(v) is np.ndarray or type(v) is list:
            r[ll] = np.percentile(r[ll], (1 - conf) / 2, axis=0)
            r[ll] = np.percentile(r[ll], 1/2 + conf/2, axis=0)

    return r_mín, r_máx


# Validar el interval de confianza
def validar_interval(d, r_mín, r_máx, conteo=None):
    if conteo is None:
        conteo = (0, 0)
    for ll, v in d.items():
        if type(v) is dict:
            validar_interval(v, r_mín[ll], r_máx[ll], conteo)
        elif type(v) is np.ndarray or type(v) is list:
            conteo[0] += sum((r_mín < v) & (v > r_máx))  # Datos que caen en el interval
            conteo[1] += len(v)  # Número total de datos

    return conteo[0]/conteo[1]
