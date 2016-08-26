import numpy as np
from pymc import *

from COSO import Coso
from RAE.REDES import Red


# Función para representar el modelo estadístico
def inic_calib(red, datos, tiempo_final, poblaciones_iniciales, paso):
    # TODO: Escribir descripción detallada de esta función aquí.
    """



    """
    # Generar variables para los parámetros del modelo

    # Primero, leer los parámetros de los diccionarios de los objetos
    def leerdic(d, l=[], init=1):
        if init == 1:
            l = []
        # Para referenciar los variables globales definidos arriba (y no locales a la función)
        if isinstance(d, Coso):
            d = d.dic
        for ll, v in sorted(d.items()):  # Para cada llave (ordenada alfabéticamente) y valor del diccionario...
            if type(v) is dict:  # Si el valor de la llave es otro diccionario:
                leerdic(v, l, init=0)  # Repetir la funcción con el nuevo diccionario
            elif isinstance(v, Coso):  # Si la llave corresponde a un objeto, leer su diccionario
                leerdic(v.dic, l, init=0)
            elif isinstance(v, int) or isinstance(v, float):  # Sólamente calibrar los parámetros numéricos
                l.append(v)
            elif isinstance(v, list):  # Si el parametro es una lista (p.ej. datos de diferentes niveles de suelo)
                for j in v:
                    l.append(j)
        return l

    lista_parámetros = []
    # Convertir el diccionario de cada insecto de la red a una lista
    for insecto in red.insectos.items():
        for fase in insecto[1].fases.items():
            lista_parámetros += leerdic(fase[1].dic["coefs"])

    matr_parámetros = np.array(lista_parámetros)  # Convertir la lista de parámetros a una matriz para PyMC

    # Una ecuación para escribir los datos del variable PyMC en el diccionario de la red

    # Para cada parámetro, una distribución normal centrada en su valor inicial con precición = tau
    parámetros = np.empty(len(matr_parámetros), dtype=object)
    tau = np.empty(len(matr_parámetros), dtype=object)
    for k in range(len(matr_parámetros)):
        tau[k] = Exponential('tau_%s' % k, beta=1.)
        parámetros[k] = Normal('parám_%s' % k, mu=matr_parámetros[k], tau=tau[k])

    # Datos observados
    núm_insectos = 0
    for insecto in datos:
        núm_insectos += len(datos[insecto])  # Para saber la dimensión necesaria para la matriz de datos
    matriz_datos = np.zeros(shape=(núm_insectos, tiempo_final))
    matriz_datos.fill(-99)  # -99 representa datos que faltan
    núm_pobs = 0
    for ins, ins_fases in sorted(datos.items()):
        for f, pobs in sorted(ins_fases.items()):
            if len(pobs) < tiempo_final:  # Si faltan datos al fin, poner valores vacíos
                pobs += ([-99] * (tiempo_final - len(pobs)))
            elif len(pobs) > tiempo_final:  # Si hay más datos que necesarios, borrar los que sobran
                pobs = pobs[:tiempo_final]
            matriz_datos[núm_pobs] = pobs
            núm_pobs += 1

    # Datos simulados (Utilizados para determinar el promedio, o valor esperado de los variables)
    @deterministic(plot=False)
    def promedio(t=tiempo_final, p=parámetros):
        # Poner los parámetros del modelo a fecha:
        escribirdic(red, parámetros=p)

        # Ejecutar el modelo. Sustraemos 1 de t porque ya tenemos el primer dato inicial
        poblaciones = red.simul(1, poblaciones_iniciales, {"Coco": 10000000}, t-1)
        egr = np.zeros(shape=(núm_insectos, t))
        núm_pob = 0
        for insecto, fases in sorted(datos.items()):  # Sólo leemos los insectos inclusos en los datos observados
            for fase in sorted(fases.items()):
                egr[núm_pob] = poblaciones[insecto][fase[0]]
                núm_pob += 1
        return egr

    # Variables estocásticos para las predicciones (se supone que las observaciones están distribuidas en una
    # distribución normal, con precisión "precisión_pobs", alrededor de la predicción del modelo).
    matriz_datos_falt = np.ma.masked_equal(matriz_datos, value=-99)
    precisión_pobs = Exponential("precisión_pobs", beta=1.)

    variables = Normal('variables', mu=promedio, tau=precisión_pobs,
                       value=matriz_datos_falt, observed=True)
    return [parámetros, tau, promedio, precisión_pobs, matriz_datos_falt, variables], \
           [len(lista_parámetros), tiempo_final, paso], red


def salvar(mod):
    M = mod.M
    red = mod[2]
    núm_parám = mod[1][0]
    parámetros = []
    for k in núm_parám:
        for i in M.trace('parám_%s' % k):
            parámetros[k].append(i)
            red.dic_incert['parám_%s' % k] = parámetros[k]
    red.dic['paso'] = mod[1][2]
    red.dic['tiempo_final'] = mod[1][1]
    red.guardar()
    escribirdic_calib(red, parámetros=parámetros)


def anal_incert(mod, datos, conf, rep, poblaciones_iniciales):
    if type(mod) is Red:
        red = mod
        núm_parám = len(red.dic_incert)
        tiempo_final = red.dic['tiempo_final']
        paso = red.dic['paso']
    elif type(mod) is tuple:
        núm_parám = mod[1][0]
        tiempo_final = mod[1][1]
        paso = mod[1][2]
        mod = mod[0]
        red = mod[2]
    else:
        return "Modelo no válido para análisis de incertidumbre (anal_incert)"

    caminos = {}
    promedios = {}
    prom_parám_lista = []
    for i in range(núm_parám):
        if type(mod) is Red:
            caminos["parám_%s" % i] = mod.dic_incert["parám_%s" % i]
        else:
            caminos["parám_%s" % i] = mod.trace("parám_%s" % i)
        prom = núm = 0
        for j in caminos["parám_%s" % i]:
            prom += j
            núm += 1
        promedios["parám_%s" % i] = prom/núm
        prom_parám_lista.append(prom/núm)

    # Poner los parámetros a sus valores promedios
    escribirdic(red, parámetros=prom_parám_lista)
    resultados_promedios = red.simul(paso, poblaciones_iniciales,
                                     estado_cultivo={"Coco": 100000}, tiempo_final=tiempo_final)

    # Poner parámetros a valores aleatorios
    res_alea = []
    import random
    if rep > len(promedios):
        print("Sólo hay" + str(len(promedios)) + "iteraciones disponibles para el análisis de incertidumbre.")
        rep = len(promedios)
    aleatorios = random.sample(range(0, len(promedios)), rep)
    for i in aleatorios:
        parám_lista = []
        for j in range(núm_parám):
            parám_lista.append(caminos["parám_%s" % j][i])
        escribirdic(red.dic, parámetros=parám_lista)
        res_alea.append(red.simul(tiempo_final))

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

    # Gráfico
    import pylab
    colores = ("red", "orange", "yellow", "green", "blue", "purple", "fuchsia", "black")
    for núm_ins, insecto in enumerate(resultados_promedios):
        pylab.figure(núm_ins + 1)
        pylab.subplots_adjust(hspace=0, right=1)
        for núm, fase in enumerate(resultados_promedios[insecto]):
            pylab.subplot(len(resultados_promedios[insecto]), 1, núm + 1)
            pylab.title = "பூச்சிகள்"
            pylab.plot(datos[insecto][fase], "o", color=colores[núm])
            pylab.plot(resultados_promedios[insecto][fase], color=colores[núm],
                       linewidth=2)
            pylab.plot(resultados_mín[insecto][fase], color=colores[núm],
                       linewidth=1, linestyle='dotted')
            pylab.plot(resultados_máx[insecto][fase], color=colores[núm],
                       linewidth=1, linestyle='dotted')
            pylab.ylabel(insecto + ", " + fase)

        pylab.xticks = (range(0, int(tiempo_final*1.1), int(tiempo_final/10)))
        pylab.xlabel('நாட்கள்')
        pylab.savefig("பயிற்சி_" + insecto + ".png")

    return por_en_inter  # Devolver el % de los datos que caen en el intervalo de confianza


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


def escribirdic_calib(d, parámetros, n=0):
    if isinstance(d, Coso):
        d = d.dic
    for ll, v in sorted(d.items()):  # Para cada llave (ordenada alfabéticamente) y valor del diccionario...
        if type(v) is dict:  # Si el valor de la llave es otro diccionario:
            escribirdic_calib(v, parámetros=parámetros, n=n)  # Repetir la funcción con el nuevo diccionario
        elif isinstance(v, Coso):  # Si la llave corresponde a un objeto, leer su diccionario
            escribirdic_calib(v.dic, parámetros=parámetros, n=n)
        elif isinstance(v, list):  # Si la llave refiere a una lista de valores
            if isinstance(v[0], int) or isinstance(v[0], float):  # Sólamente calibrar los parámetros numéricos
                d[ll].append(parámetros[n])
                n += 1
            elif isinstance(v[0], list):
                for j in v:
                    d[ll][j].append = parámetros[n]
                    n += 1
    return d
