# Este documento contiene las funciones de manejo de datos de clima
import datetime as ft
import json
import os

import numpy as np
from geopy.distance import vincenty as dist


# Una función para leer los datos de clima de un documento especificado
def cargar_estación(documento, coord, elev, fecha_inic=None, fecha_fin=None, generar=True):
    """
    Limitaciones: 1) Al momento, solamente se leen documentos .csv de formato INSIVUMEH o con nombres de columnas
    Y UNIDADES iguales a los utilizados aquí: Fecha, [Hora], Precip (mm), Rad_sol (MJ/m2/día), y Temp (C).
    :param documento:
    :param coord:
    :param elev:
    :param fecha_inic:
    :param fecha_fin:
    :param generar:
    :return:
    """

    # Para guardar los datos extraídos
    dic = dict(Elev=elev, Coord=coord, Fecha=[], Datos=dict(Precip=[], Rad_sol=[], Temp_máx=[], Temp_mín=[]))

    # Para guardar índices de los datos que faltan
    faltan = False
    faltan_puntos = dic['Datos'].copy()
    faltan_porciones = dic['Datos'].copy()

    # Para guardar las fechas y horas de los datos
    fechatiempos = []
    if '.día' in documento:  # Si el documento ya es un objeto "diario" guardado
        dic = json.load(documento)
        for n, f in enumerate(dic['Fecha']):
            dic['Fecha'][n] = (ft.datetime(f[2], f[1], f[0]))
    elif '.csv' in documento:  # Si el documento todavía se encuentra en forma .csv
        # (al momento, sólo lee formato de la INSIVUMEH)
        insivumeh = False

        # Para guardar datos de climar horarios
        precip_hora = temp_hora = rad_sol_hora = []

        with open(documento) as d:
            doc = d.readlines()
        variables = doc[0].split(',')
        conv_var_insivumeh = {'Lluvia': 'Precip', 'R.Global': 'Rad_sol', 'Temp.Ai': 'Temp'}
        # Convertir nombres de variables del formato INSIVUMEH hacia el formato Tikon
        for n, var in enumerate(variables):
            if '[w/m2]' in var:
                insivumeh = True
            for var_INSI in conv_var_insivumeh:
                if var_INSI in var:
                    variables[n] = conv_var_insivumeh[var_INSI]

        # Leer los datos
        for i in doc[1:]:
            datos = i.split(',')
            # Leer la fecha y la hora, si aplica
            f = datos[variables.index('Fecha')].split('/')
            fechatiempos.append(ft.datetime(int(f[2]), int(f[1]), int(f[0])))
            if 'Hora' in variables:
                h = datos[variables.index('Hora')].split(':')
                fechatiempos[-1] = fechatiempos[-1].replace(hour=int(h[0]), minute=int(h[1]), second=int(h[2]))

            # Convertir los datos vacíos a 'NaN'
            precip = variables.index('Precip')
            rad_sol = variables.index('Rad_sol')
            temp = variables.index('Temp')
            for var in [precip, rad_sol, temp]:
                if datos[var] == '':
                    datos[var] = float('NaN')

            precip_hora.append(float(precip))
            rad_sol_hora.append(float(rad_sol))
            temp_hora.append(float(temp))

        # Conversiones unidades INSIVUMEH
        if insivumeh:
            rad_sol_hora = [i * 0.0036 for i in rad_sol_hora]  # 0.0036 W por MJ

        # Inicializar los variables diarios
        lluvia_cum = precip_hora[0]
        rad_sol_cum = rad_sol_hora[0]
        temp_día = [temp_hora[0]]

        # Convertir datos horarios a datos diario
        for n, i in enumerate(fechatiempos[1:]):
            if i.date() == fechatiempos[n-1].date():
                # Sumar la lluvia y la radiación solar
                lluvia_cum += precip_hora[n]
                rad_sol_cum += (rad_sol_hora[n] + rad_sol_hora[n-1]) * \
                               (fechatiempos[n].hour - fechatiempos[n-1].hour) / 2  # Interpolación trapezoidal
                # Hacer una lista de las temperaturas en el día
                temp_día.append(temp_hora[n])
            else:
                dic['Datos']['Precip'].append(lluvia_cum)
                lluvia_cum = precip_hora[n+1]
                dic['Datos']['Rad_sol'].append(rad_sol_cum)
                rad_sol_cum = rad_sol_hora[n+1]
                dic['Datos']['Temp_mín'].append(min(temp_día))
                dic['Datos']['Temp_máx'].append(max(temp_día))
                temp_día = [temp_hora[n+1]]
                dic['Datos']['Fecha'].append(fechatiempos[n].date())

    else:  # Si el documento es ni un .csv, ni un objeto de datos diarios guardado
        return False

    # Si no queremos generar datos que faltan (si vamos a utilizar esta estación para estimar a otra)
    if not generar:
        return ordenar(dic)

    # Si no se especificaron fechas de inicio o de fin, utilizar el rango de datos disponibles:
    if fecha_inic is None:
        fecha_inic = min(dic['Fecha'])
    if fecha_fin is None:
        fecha_fin = max(dic['Fecha'])

    # Añadir líneas vacías para fechas entierras que faltan
    f = fecha_inic
    while f <= fecha_fin:
        if f not in dic['Fecha']:
            dic['Fecha'].append(f)
            for var in dic['Datos']:
                # Poner valores vaciós para los variables
                dic['Datos'][var].append(float('NaN'))
    # ... y ya que tenemos listas del mismo tamaño para cada variable (y las fechas), cambiarlos a matrices numpy
    dic = ordenar(dic)  # Primero, ordenar los datos según su fecha
    for var in dic['Datos']:
        dic[var] = np.array(dic[var])

    # Verificar si faltan datos para variables individuales:
    for var in dic['Datos']:
        for n, i in enumerate(dic['Datos'][var]):
            if np.isnan(i):  # Si falta el valor, añadir la fecha a la lista de datos que faltan
                faltan_puntos[var].append(dic['Datos'][var]['Fecha'][n])
                faltan = True  # Marcador para indicar que hay al menos un dato a estimar

    # Verificar si faltan grandes extensiones (más de 10 días consecutivos) de datos
    while n < len(faltan_puntos[var]):
        consecutivos = 0
        while (faltan_puntos[var][n+1] - faltan_puntos[var][n]).days == 1:
            consecutivos += 1
            n += 1
        if consecutivos >= 9:
            faltan_porciones[var] += (faltan_puntos[var][n-consecutivos], faltan_puntos[var][n])

    for i in faltan_porciones[var]:  # Quitar estas fechas de la lista de datos puntuales que faltan
        faltan_puntos[var].pop(faltan_puntos[var].index(i))

    return dic, faltan, faltan_puntos, faltan_porciones


# Esta función ordena los datos según su fecha
def ordenar(dic):
    a_ordenar = [dic['Fecha']]
    variables = sorted(list(dic['Datos'].keys()))
    for var in variables:
        a_ordenar.append(dic['Datos'][var])

    # Lambda asegura que ordenemos por la fecha
    ordenados = [x for x in sorted(zip(a_ordenar), key=lambda dato: dato[0])]
    ordenados = list(zip(*ordenados))

    for n, var in a_ordenar[1:]:
        dic['Datos'][var] = ordenados[n]
    dic['Fecha'] = ordenados[0]

    return dic


# Una función para buscar n estaciones cercanas a un punto especificado
def buscar_cercanas(n, coord, estaciones):
    nombres_cercanas = distancias = []

    for i in estaciones:
        # Calcular la distancia entre la estación y el punto de interés
        distancia = dist((estaciones[i]['Lat'], estaciones[i]['Long']), coord).km
        # Si encontramos una mejora estación o no hemos llegado a n estaciones
        if distancia < max(distancias) or len(nombres_cercanas) < n:
            # Si ya tenemos una lista de n estaciones, quitar la estación la más lejana
            if len(nombres_cercanas) >= n:
                índice = distancias.index(max(distancias))
                nombres_cercanas.pop(índice)
                distancias.pop(índice)
            # Añadir la nueva estación
            distancias.append(distancia)
            nombres_cercanas.append(estaciones[i]['Estación'])

    # Leer los datos de las n estaciones más cercanas
    estaciones_cercanas = []
    for i in nombres_cercanas:
        estaciones_cercanas.append(
            cargar_estación(os.path.join('Proyectos', 'Clima', i, '.csv'), generar=False)[0]
        )
    return estaciones_cercanas


# Una función para verificar si las estaciones tienen los datos necesarios para estimar los datos a una otra estación
def verificar_fechas(var, estaciones, fechas):
    """
    var: nombre de la variable
    estaciones: lista de los diccionarios de datos de las estaciones a verificar
    fechas: lista de fechas de datos que faltan
    """
    verificados = []
    for estación in estaciones:
        for fecha in fechas:
            if fecha in estación['Fecha']:
                if not np.isnan(estación[var][estaciones['Fecha'].index(fecha)]):
                    verificados.append(estación)
                    break

    return verificados  # Devolver las estaciones con al menos una fecha de interés
