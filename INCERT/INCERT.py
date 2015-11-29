import numpy as np
import random as aleatorio

from COSO import Coso
from INCERT.CALIB import extraer_objetos, leerdatos


# Este módulo maneja el análisis de incertidumbre de los modelos.


def anal_incert(objeto, opciones_simul, conf=0.95, rep=100, tiempo_inic=None, tiempo_fin=None, datos=None):

    if not isinstance(objeto, Coso):
        raise TypeError('anal_incert requiere un objeto de tipo "Coso".')

    simul = objeto.simul

    # Calcular los tiempos iniciales y finales
    if datos is None:
        if hasattr(objeto, 'datos'):
            datos = objeto.datos
            lista_obs, matriz_tiempos = leerdatos(datos)
            if tiempo_fin is None:
                tiempo_fin = [t.max for t in matriz_tiempos]
            if tiempo_inic is None:
                tiempo_inic = [t.min for t in matriz_tiempos]
        else:
            datos = {}
            if tiempo_fin is None or tiempo_inic is None:
                return 'Se necesita ingresar fechas para el análisis de incertidumbre.'

    if type(tiempo_fin) is int or type(tiempo_fin) is float:
        tiempo_fin = [tiempo_fin]
    if type(tiempo_inic) is int or type(tiempo_inic) is float:
        tiempo_inic = [tiempo_inic]

    lista_objetos = extraer_objetos(objeto)

    núm_total = núm_en_inter = 0
    lista_res_alea = []
    for exp in sorted(datos.keys()):
        # Poner parámetros a valores aleatorios
        res_alea = []
        for objeto in lista_objetos:
            n_iter = len(objeto.dic_incert[objeto.dic_incert.keys()[0]])  # El número de iteraciones en dic_incert.
            # Si se pidieron más repeticiones que haya iteraciones en dic_incert,
            # tomar el número de iteraciones disponibles
            if rep > n_iter:
                print("Aviso: Sólo hay %s iteraciones disponibles para el análisis de incertidumbre." % n_iter)
                rep = n_iter
            aleatorios = aleatorio.sample(range(0, n_iter), rep)
            for i in aleatorios:
                escoger_parám(objeto.dic, objeto.dic_incert, n=i)

        res_alea.append(simul(tiempo_inic=tiempo_inic, tiempo_final=tiempo_fin, **opciones_simul))

        # Cambiar el formato de los resultados para que cada valor del variable sea una matriz numpy 2D con una línea
        # de la matriz para cada corrida.
        res_alea = arreglar_resultados(res_alea)
        lista_res_alea.append(res_alea)

        # Calcular los límites de los intervales de confianza
        resultados_mín, resultados_máx = calc_intervalos(res_alea, conf)

        # Calcular el % de los datos que caen en el interval de confianza
        res_inter = validar_intervalo(datos[exp], resultados_mín, resultados_máx)
        núm_total += res_inter[1]
        núm_en_inter += res_inter[0]

    # Devolver el % de los datos que caen en el interval de confianza y los resultados de las corridas
    return núm_en_inter/núm_total, lista_res_alea


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


def escoger_parám(d, d_i, n):
    for ll, v in d.items():  # Para cada llave y valor del diccionario...
        if type(v) is dict:  # Si el valor de la llave es otro diccionario:
            escoger_parám(v, d_i[ll], n)  # Repetir la funcción con el nuevo diccionario
        elif isinstance(v, int) or isinstance(v, float):  # Sólamente incluir los parámetros numéricos
            d[ll] = d_i[ll][n]
        # Si la llave refiere a una lista de valores
        elif type(v) is list and (type(v[0]) is float or type(v[0]) is int):
            for j in v:
                d[ll][j] = d_i[ll][j][n]


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
def calc_intervalos(r, conf, r_mín=None, r_máx=None):
    if r_mín is None:
        r_mín = r.copy()
    if r_máx is None:
        r_máx = r.copy()
    for ll, v in r.items():
        if type(v) is dict:
            calc_intervalos(v, conf, r_mín[ll], r_máx[ll])
        elif type(v) is np.ndarray or type(v) is list:
            r[ll] = np.percentile(r[ll], (1 - conf) / 2, axis=0)
            r[ll] = np.percentile(r[ll], 1/2 + conf/2, axis=0)

    return r_mín, r_máx


# Validar el interval de confianza
def validar_intervalo(d, r_mín, r_máx, conteo=None):
    if conteo is None:
        conteo = (0, 0)
    for ll, v in d.items():
        if type(v) is dict:
            validar_intervalo(v, r_mín[ll], r_máx[ll], conteo)
        elif type(v) is np.ndarray or type(v) is list:
            conteo[0] += sum((r_mín < v) & (v > r_máx))  # Datos que caen en el interval
            conteo[1] += len(v)  # Número total de datos

    return conteo[0], conteo[1]
