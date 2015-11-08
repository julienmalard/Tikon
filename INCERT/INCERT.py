import numpy as np
import random as aleatorio


# Este módulo maneja el análisis de incertidumbre de los modelos.


def anal_incert(dic_incert, modelo, datos, conf=0.95, rep=100):

    lista_parám = sacar_parám(dic_incert)

    dic = sacar_llaves(dic_incert)
    # Poner los parámetros a sus valores promedios
    promedios = []
    for i in lista_parám:
        promedios.append(np.average(i))

    dic = escribir_parám(dic, parámetros=promedios)
    resultados_promedios = modelo(***parámetros)

    # Poner parámetros a valores aleatorios
    res_alea = []
    if rep > len(promedios):
        print("Sólo hay" + str(len(promedios)) + "iteraciones disponibles para el análisis de incertidumbre.")
        rep = len(promedios)
    aleatorios = aleatorio.sample(range(0, len(promedios)), rep)
    for i in aleatorios:
        paráms = []
        for j in range(len(lista_parám)):
            paráms.append(lista_parám[j][i])
        dic = escribir_parám(dic, parámetros=paráms)
        res_alea.append(modelo(***parámetros))

    resultados_mín = resultados_máx = {}
    for insecto in datos:
        resultados_mín[insecto] = {}
        resultados_máx[insecto] = {}
        for fase in datos[insecto]:
            matr = np.empty(shape=(tiempo_final+1))
            # Convertir el diccionario de resultados a una matriz numpy
            for repl in res_alea:
                matr_temp = np.array(repl[insecto][fase])
                matr = np.vstack((matr, matr_temp))
            resultados_mín[insecto][fase] = np.percentile(matr, (1-conf)/2, axis=0)
            print(fase, "mínimo", np.percentile(matr, (1-conf)/2, axis=0))
            resultados_máx[insecto][fase] = np.percentile(matr, 1/2 + conf/2, axis=0)
            print(fase, "máximo", np.percentile(matr, 1/2 + conf/2, axis=0))

    # Calcular el % de los datos que caen en el intervalo de confianza
    dat_correcto = dat_total = 0
    for insecto in datos:
        for fase in datos[insecto]:
            for día, pob in enumerate(datos[insecto][fase]):  # Para cada día de datos observados...
                if pob != -99:  # Si el dato observado no falta...
                    if resultados_mín[insecto][fase][día] <= pob <= resultados_máx[insecto][fase][día]:
                        dat_correcto += 1
                    dat_total += 1
    por_en_inter = dat_correcto/dat_total

    def filtrarresultados(r, d, f=None):
        if not f:
            f = []
        for ll, v in sorted(d.items()):
            if type(v) is dict:  # Si el valor de la llave es otro diccionario:
                filtrarresultados(r[ll], v, f)  # Repetir la función con el nuevo diccionario
            elif isinstance(v, tuple):  # Si encontramos los datos
                f += [x for n, x in enumerate(r[ll]) if n in v[0]]

        return f

    return por_en_inter  # Devolver el % de los datos que caen en el intervalo de confianza


def sacar_llaves(d, l=None):
    if not l:
        l = []

    for ll, v in d.items():
        l.append(ll)
        if type(v) is dict:
            sacar_llaves(d, l=l)

    return l


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
    return d
