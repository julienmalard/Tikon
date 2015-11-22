import numpy as np
from pymc import Normal, Exponential, deterministic, MCMC

from COSO import Coso


def genmodbayes(datos, diccionarios, simul):
    # TODO: Escribir descripción detallada de esta función aquí.
    """

    :param datos:
    :param diccionarios: una lista de los diccionarios de parámetros que hay que calibrar.
    :param simul:
    :return:
    """
    # Generar variables para los parámetros del modelo

    # Primero, leer los parámetros de los diccionarios de los objetos
    # Incorporar los parámetros de todos los diccionario en una lista
    lista_parámetros = []
    for dic in diccionarios:
        lista_parámetros += leerdic(dic)
    matr_parámetros = np.array(lista_parámetros)  # Convertir la lista de parámetros a una matriz para PyMC

    # Para cada parámetro, una distribución normal centrada en su valor inicial con precición = tau
    parámetros = np.empty(len(matr_parámetros), dtype=object)
    tau = np.empty(len(matr_parámetros), dtype=object)
    for k in range(len(matr_parámetros)):
        tau[k] = Exponential('tau_%s' % k, beta=1.)
        parámetros[k] = Normal('parám_%s' % k, mu=matr_parámetros[k], tau=tau[k])

    # Guardar los datos de manera reproducible en una única lista
    lista_datos, lista_tiempos = leerdatos(datos)
    lista_datos = np.array(lista_datos)
    lista_tiempos = np.array(lista_tiempos)

    tiempo_final = max(lista_tiempos)  # Calcular el tiempo final según los datos observados

    # Datos simulados (Utilizados para determinar el promedio, o valor esperado de los variables)
    @deterministic(plot=False)
    def promedio(t=tiempo_final, p=parámetros):
        # Poner los parámetros del modelo a fecha:
        escribirdic(diccionarios, parámetros=p)

        # Ejecutar el modelo.
        resultados = simul(tiempo_final=t)
        egr = np.array(filtrarresultados(resultados, datos))  # La lista de egresos del modelo

        return egr

    # Variables estocásticos para las predicciones (se supone que las observaciones están distribuidas en una
    # distribución normal, con precisión "precisión", alrededor de la predicción del modelo).
    precisión = Exponential("precisión", beta=1.)

    variables = Normal('variables', mu=promedio, tau=precisión, value=lista_datos, observed=True)
    return [parámetros, tau, promedio, precisión, lista_datos, variables]


def leerdic(d, l=None):
        if not l:
            l = []
        if isinstance(d, Coso):
            d = d.dic
        for ll, v in sorted(d.items()):  # Para cada llave (ordenada alfabéticamente) y valor del diccionario...
            if type(v) is dict:  # Si el valor de la llave es otro diccionario:
                leerdic(v, l)  # Repetir la funcción con el nuevo diccionario
            elif isinstance(v, Coso):  # Si la llave corresponde a un objeto, leer su diccionario
                leerdic(v.dic, l)
            elif isinstance(v, int) or isinstance(v, float):  # Sólamente calibrar los parámetros numéricos
                l.append(v)
            elif isinstance(v, list):  # Si el parametro es una lista (p.ej. datos de diferentes niveles de suelo)
                l += v
        return l


def escribirdic(d, parámetros, n=0):
    if isinstance(d, Coso):
        d = d.dic
    for ll, v in sorted(d.items()):  # Para cada llave (ordenada alfabéticamente) y valor del diccionario...
        if type(v) is dict:  # Si el valor de la llave es otro diccionario:
            escribirdic(v, parámetros=parámetros, n=n)  # Repetir la funcción con el nuevo diccionario
        elif isinstance(v, Coso):  # Si la llave corresponde a un objeto, leer su diccionario
            escribirdic(v.dic, parámetros=parámetros, n=n)
        elif isinstance(v, int) or isinstance(v, float):  # Sólamente calibrar los parámetros numéricos
            d[ll] = parámetros[n].value
            n += 1
        elif isinstance(v, list):  # Si la llave refiere a una lista de valores
            for j in v:
                d[ll][j] = parámetros[n].value
                n += 1
    return d


def leerdatos(d, l=None, t=None):
    if not l:
        l = []  # Los datos
        t = []  # tiempo de los datos
    for ll, v in sorted(d.items()):
        if type(v) is dict:  # Si el valor de la llave es otro diccionario:
            leerdatos(v, l, t)  # Repetir la funcción con el nuevo diccionario
        elif isinstance(v, tuple):  # Si encontramos los datos
            l += v[0]
            t += v[1]

    return l, t


def filtrarresultados(r, d, f=None):
    """
    Esta función toma diccionarios de resultados de simulación y de datos observados y devuelve una lista ordenada de
    los datos de simulación correspondiendo a los puntos para cuales tenemos los datos observados.
    :param r: diccionario de resultados de simulación, de la forma {var1: [(fecha, dato), (fecha, dato)...], var2: ...}.
    Puede contener un número arbitrario de diccionarios adentro del diccionario de datos.
    :param d: un diccionario de datos observados, de la misma forma. No es necesario tener todas las llaves de r en d.
    :param f: el diccionario de los datos filtrados
    :return: f
    """
    if not f:
        f = []
    for ll, v in sorted(d.items()):
        if type(v) is dict:  # Si el valor de la llave es otro diccionario...
            filtrarresultados(r[ll], v, f)  # ...repetir la función con el nuevo diccionario
        elif isinstance(v, tuple):  # Si encontramos los datos...
            r[ll].sort()  # Asegurarse que el tiempo va para adelante
            f += [x for n, x in enumerate(r[ll]) if n in v[0]]  # Sacar los puntos para cuales tenemos datos

    return f


def calib(modelo, it, quema, espacio):
    m = MCMC(modelo)
    m.sample(iter=it, burn=quema, thin=espacio)

    return m


def guardar(calibrado, dic_incert):

    parámetros = {}
    for k in nombres:
        for i in calibrado.trace(k):
            parámetros[k].append(i)
            dic_incert['parám_%s' % k] = parámetros[k]
