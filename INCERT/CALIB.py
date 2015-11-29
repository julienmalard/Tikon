import numpy as np
from pymc import Normal, Exponential, deterministic, MCMC

from COSO import Coso


def genmodbayes(objeto, opciones_simul):
    # A hacer: Escribir descripción detallada de esta función aquí.
    """

    :param opciones_simul:
    :param objeto:
    :return:
    """
    datos = objeto.datos
    simul = objeto.simul

    # Generar variables para los parámetros del modelo

    # Primero, leer los parámetros de los diccionarios de los objetos
    # Incorporar los parámetros de todos los diccionario en una lista
    lista_objetos = extraer_objetos(objeto)
    lista_parámetros = []
    for obj in lista_objetos:
        lista_parámetros += leerdic(obj)
    matr_parámetros = np.array(lista_parámetros)  # Convertir la lista de parámetros a una matriz para PyMC

    # Para cada parámetro, una distribución normal centrada en su valor inicial con precición = tau
    parámetros = np.empty(len(matr_parámetros), dtype=object)
    tau = np.empty(len(matr_parámetros), dtype=object)
    for k in range(len(matr_parámetros)):
        tau[k] = Exponential('tau_%s' % k, beta=1.)
        parámetros[k] = Normal('parám_%s' % k, mu=matr_parámetros[k], tau=tau[k])

    # Guardar los datos de manera reproducible en una única lista
    experimentos = sorted(datos.keys())
    lista_datos, matriz_tiempos = leerdatos(datos)

    tiempos_finales = [t.max for t in matriz_tiempos]  # Calcular el tiempo final según los datos observados

    # Datos simulados (Utilizados para determinar el promedio, o valor esperado de los variables)
    @deterministic(plot=False)
    def promedio(t=tiempos_finales, p=parámetros, o=opciones_simul):
        # Poner los parámetros del modelo a fecha:
        escribirdics(lista_objetos, parámetros=p)

        # Ejecutar el modelo.
        egr = []
        for n, exp in enumerate(experimentos):
            resultados = simul(tiempo_final=t[n], **o)
            egr += filtrarresultados(resultados, datos[exp])  # La lista de egresos del modelo

        return np.array(egr)

    # Variables estocásticos para las predicciones (se supone que las observaciones están distribuidas en una
    # distribución normal, con precisión "precisión", alrededor de la predicción del modelo).
    precisión = Exponential("precisión", beta=1.)

    variables = Normal('variables', mu=promedio, tau=precisión, value=lista_datos, observed=True)
    return [parámetros, tau, promedio, precisión, lista_datos, variables]


def extraer_objetos(d, l=None):
    if l is None:
        l = []
    if isinstance(d, Coso):
        d = d.objetos
    for ll, v in sorted(d.items()):
        if isinstance(v, Coso):
            l += v
        extraer_objetos(v, l=l)

    return l


def leerdic(d, l=None):
    if l is None:
        l = []
    for ll, v in sorted(d.items()):  # Para cada llave (ordenada alfabéticamente) y valor del diccionario...
        if type(v) is dict:  # Si el valor de la llave es otro diccionario:
            leerdic(v, l)  # Repetir la funcción con el nuevo diccionario
        elif isinstance(v, int) or isinstance(v, float):  # Sólamente calibrar los parámetros numéricos
            l.append(v)
        elif isinstance(v, list):  # Si el parametro es una lista (p.ej. datos de diferentes niveles de suelo)
            for j in v:
                if type(j) is int or type(j) is float:
                    l.append(j)
    return l


def escribirdic(d, parámetros, n=0):
    for ll, v in sorted(d.items()):  # Para cada llave (ordenada alfabéticamente) y valor del diccionario...
        if type(v) is dict:  # Si el valor de la llave es otro diccionario:
            escribirdic(v, parámetros=parámetros, n=n)  # Repetir la funcción con el nuevo diccionario
        elif isinstance(v, int) or isinstance(v, float):  # Sólamente calibrar los parámetros numéricos
            d[ll] = parámetros[n].value
            n += 1
        elif isinstance(v, list):  # Si la llave refiere a una lista de valores
            for m, j in enumerate(v):
                if type(j) is int or type(j) is float:
                    d[ll][m] = parámetros[n].value
                    n += 1
    return n


def escribirdics(objetos, parámetros):
    n = 0
    for obj in objetos:
        n = escribirdic(obj.dic, parámetros=parámetros, n=n)


def leerdatos(datos):
    lista_datos = []
    matriz_tiempos = []
    for exp in datos:
        extraidos = extraer_datos(exp)
        lista_datos += extraidos[0]
        matriz_tiempos.append(extraidos[1])

    return lista_datos, matriz_tiempos


def extraer_datos(d, l=None, t=None):
    if l is None:
        l = []  # Los datos
        t = []  # tiempo de los datos
    for ll, v in sorted(d.items()):
        if type(v) is dict:  # Si el valor de la llave es otro diccionario:
            extraer_datos(v, l, t)  # Repetir la funcción con el nuevo diccionario
        elif isinstance(v, tuple):  # Si encontramos los datos
            t += v[0]
            l += v[1]
    return l, t


def filtrarresultados(r, d, f=None):
    """
    Esta función toma diccionarios de resultados de simulación y de datos observados y devuelve una lista ordenada de
    los datos de simulación correspondiendo a los puntos para cuales tenemos los datos observados.

    :param r: diccionario de resultados de simulación, de la forma {var1: [(fecha, dato), (fecha, dato)...], var2: ...}.
    Puede contener un número arbitrario de diccionarios adentro del diccionario de datos.

    :param d: un diccionario de datos observados, de la misma forma. No es necesario tener todas las llaves de r en d.

    :param f: la lista con los datos filtrados

    :return: f
    """

    if f is None:
        f = []
    for ll, v in sorted(d.items()):
        if type(v) is dict:  # Si el valor de la llave es otro diccionario...
            filtrarresultados(r[ll], v, f)  # ...repetir la función con el nuevo diccionario
        elif type(v) is tuple:  # Si encontramos los datos...
            ordenados = list(enumerate(r[ll]))
            ordenados.sort()  # Asegurarse que el tiempo va para adelante
            f += [x for n, x in ordenados if n in v[0]]  # Sacar los puntos para cuales tenemos datos

    return f


# Esta función corre la calibración Bayesiana basado en un modelo generado por genmodbayes()
def calib(modelo, it, quema, espacio):
    m = MCMC(modelo)
    m.sample(iter=it, burn=quema, thin=espacio)

    return m


# Esta función guarda los resultados de una calibración en el diccionario de incertidumbre del objeto
def guardar(calibrado, objeto):
    lista_objs = extraer_objetos(objeto)
    n = 0
    for obj in lista_objs:
        n = escribir_dic_incert(obj.dic, obj.dic_incert, calibrado=calibrado, n=n)

    objeto.guardar()


def escribir_dic_incert(d, d_i, calibrado, n=0):
    """

    :param d:
    :param d_i:
    :param calibrado:
    :param n:
    :return:
    """

    for ll, v in sorted(d.items()):  # Para cada llave (ordenada alfabéticamente) y valor del diccionario...
        if type(v) is dict:  # Si el valor de la llave es otro diccionario:
            escribir_dic_incert(v, d_i[ll], calibrado, n=n)  # Repetir la funcción con el nuevo diccionario
        elif isinstance(v, int) or isinstance(v, float):  # Sólamente calibrar los parámetros numéricos
            d_i[ll] = list(calibrado.trace(n))
            n += 1
        elif isinstance(v, list):  # Si la llave refiere a una lista de valores
            for m, j in enumerate(v):
                if type(j) is int or type(j) is float:
                    d[ll][m] = list(calibrado.trace(n))
                    n += 1
    return n
