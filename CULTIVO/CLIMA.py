import os
import json
import numpy as np
from scipy import stats as estad
from geopy.distance import vincenty as dist
import datetime as ft
from COSO import Coso


# Esta clase representa la meteo diaria en un lugar específico.
class Diario(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada suelo
        simismo.dic_base = dict(Lugar=[], Cód_lugar=[], Lat=[], Long=[], Elev=[], Temp_prom=[], Alt_med_temp=[],
                                Alt_med_viento=[], Amp_temp_mens=[], Fecha=[], Rad_sol=[], Temp_máx=[], Temp_mín=[],
                                Precip=[], Temp_conden=[], Viento=[], Rad_foto=[], Hum_rel=[])

        super().__init__(*args, **kwargs)  # Esta variable se initializa como Coso
        simismo.ext = "día"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)

        simismo.lugar = simismo.dic['Lugar']
        simismo.coord = (simismo.dic['Lat'], simismo.dic['Long'])

    def buscar(simismo, fecha_inic, fecha_fin):

        encontrado = faltan_pt = faltan_por = generamos = False
        # Buscar en los datos de clima de Python
        with open(os.path.join('Proyectos', 'Clima', 'Estaciones.csv')) as d:
            estaciones = d.readlines()
            datos_estación = estaciones[0].split(';')
            col_estación = datos_estación.index('Estación')
            col_long = datos_estación.index('Longitud')
            col_lat = datos_estación.index('Latitud')
            col_municipio = datos_estación.index('Municipio')
            for i in estaciones:
                datos_estación = i.split(';')
                # Si hay una estación con el mismo nombre:
                if datos_estación[col_estación] == simismo.lugar:
                    encontrado = True
                    break
                # Sino, si hay una estación con las mismas coordinadas:
                elif datos_estación[col_lat] == simismo.coord[0] and datos_estación[col_long] == simismo.coord[1]:
                    encontrado = True
                    break
                # O si hay una estación con el mismo nombre de municipio que no esté muy lejos:
                elif datos_estación[col_municipio] == simismo.lugar and (): # todo: calcular distancia entre estaciones
                    encontrado = True
                    break
            if encontrado:
                estación = datos_estación[col_estación]
                directorio = os.path.join('Proyectos', 'Clima', estación, '.csv')
                faltan_pt, faltan_por, dic = simismo.leer_estación(directorio, fecha_inic, fecha_fin)
                if not (faltan_pt and faltan_por):
                    return  # Si ya lo encontramos sin datos que faltan, parar aquí

        # Si no encontramos la estación, o si faltan datos
        if not encontrado or (faltan_pt and faltan_por):
            # Buscar a ver si ya tenemos datos generados para la estación
            for doc_meteogen in os.listdir(os.path.join('Proyectos', 'Clima', 'Generados')):
                if doc_meteogen.lower().endswith(".día") and simismo.lugar.lower() in doc_meteogen.lower():
                    encontrado = True
                    directorio = os.path.join('Proyectos', 'Clima', 'Generados', doc_meteogen)
                    faltan_pt, faltan_por, dic = simismo.leer_estación(directorio, fecha_inic, fecha_fin)
                    if not (faltan_pt and faltan_por):
                        return  # Si ya lo encontramos sin datos que faltan, parar aquí
                    break

        # Definir las funciones de Bahaa Khalil para generar datos que faltan
        def move1(x, y):
            # Hirsch,R.M. (1982). A comparison of four streamflow record extension
            # techniques, Water Resources Research, 18, 1081 – 1088, 1982.
            x = np.array(x)
            y = np.array(y)
            r = np.correlate(y,x)

            b_move = np.std(y) / np.std(x)
            if r < 0:
                b_move *= -1
            a_move = np.nanmean(y) - (b_move * np.nanmean(x))
            return a_move[0], b_move[0]

        def ktrl(x, y):
            # KTRL = Kendall-Theil Robust Line
            x = np.array(x)
            y = np.array(y)

            w = x.size()
            k = []
            for i in range(w-1, 1, -1):
                for j in range(0, i-2):
                    yk = y[i]-y[j]
                    xk = x[i]-x[j]
                    k.append(yk / xk)

            k = np.array(k)
            b_ktrl = np.median(k)
            a_ktrl = np.nanmedian(y)-(b_ktrl*(np.nanmedian(x)))

            return a_ktrl[0], b_ktrl[0]

        def ktrl2(x, y):
            # Modificacion del KTRL (KTRL2) desarrollado por Khalil et al (2012)
            # Khalil,B.,T.B.M.J.Ouarda,and A.St-Hilaire(2012). Comparison of
            # record-extension techniques water quality variables, Water Resources
            # Management, 26(14), 4259-4280.

            x = np.array(x)
            y = np.array(y)

            qx = np.percentile(x, [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
                                   0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95])
            qy = np.percentile(y, [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
                                   0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95])

            k2 = []
            for i in range(18, 1, -1):
                for j in range(0, i-2):
                    yk2 = qy[i]-qy[j]
                    xk2 = qx[i]-qx[j]
                    k2.append(yk2/xk2)

            k2 = np.array(k2)
            b_ktrl2 = np.nanmedian(k2)
            a_ktrl2 = np.nanmedian(y)-(b_ktrl2*(np.nanmedian(x)))

            return a_ktrl2[0], b_ktrl2[0]

        def rloc(x, y):
            # Robust Line of Organic Correlation (RLOC) desarrollado por Khalil and Adamowski (2012)

            # Khalil, B. and Adamowski, J. (2012). Record extension for short-gauged
            # water quality parameters using a newly proposed robust version of the line
            # of organic correlation technique, Hydrol. Earth Syst. Sci., 16, 2253-2266.

            x = np.array(x)
            y = np.array(y)

            r = np.correlate(y,x)

            qx = np.percentile(x, [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
                                  0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95])
            qy = np.percentile(y, [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
                                  0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95])

            b_rloc = (qy[14]- qy[4])/(qx[14]- qx[4])
            if r < 0:
                b_rloc *= -1
            a_rloc = np.nanmedian(y)-(b_rloc*(np.nanmedian(x)))

            return a_rloc[0], b_rloc[0]

        def reg_lin(x, y):
            x = np.array(x)
            y = np.array(y)
            pendiente, intersección = estad.linregress(x, y)[0:2]
            return pendiente, intersección

        if encontrado:  # Si ya encontramos una estación...
            if faltan_pt:  # ...y si faltan puntos puntuales:
                # todo: buscar estación cercana

                distancias[] = dist((), simismo.coord).km
                # todo: Verificar para valores atípicas
                if valores_atípicas:
                    a, b = ktrl(simismo.dic[variable], otraestación.dic[variable])
                # todo: Análisis Bahaa Khalil rellenar puntos
                else:
                    a, b = reg_lin(simismo.dic[variable], otraestación.dic[variable])

                # Generar números aleatorios de 10% de los datos disponibles
                estimaciones = a + b * conocidos
                r2 = np.corrcoef(estimaciones, conocidos) ** 2
                if r2 >= 0.90:
                    generamos = True  # Marcar que hemos generado datos
                    faltan_pt = False  # Marcar que ya no faltan puntos

            if faltan_por:  # Si faltan grandes porciones de datos
                # todo: buscar estación cercana

                # todo: Verificar para valores atípicas
                if valores_atípicas:
                    a, b = ktrl2(simismo.dic[variable], otraestación.dic[variable])
                # todo: Análisis Bahaa Khalil rellenar puntos
                else:
                    a, b = move1(simismo.dic[variable], otraestación.dic[variable])

                # Quitar el 10% contínuo de los datos disponibles en un lugar aleatorio
                estimaciones = a + b * conocidos
                r2 = np.corrcoef(estimaciones, conocidos) ** 2
                if r2 >= 0.90:
                    generamos = True  # Marcar que hemos generado datos
                    faltan_pt = False  # Marcar que ya no faltan puntos


        # Si no encontramos una estación o no logramos generar los datos necesarios, utilizar kriging
        if not encontrado or faltan_pt or faltan_por:
            pass
            # TODO: kriging

        # Si generamos datos, salvar el objeto en la base de datos generados de Python
        if generamos:
            simismo.escribir(os.path.join('Proyectos', 'Clima', 'Generado', simismo.lugar, '.día'))

    # Una función para leer los datos de clima de un documento especificado
    def leer_estación(simismo, documento, fecha_inic=None, fecha_fin=None):
        # Limitaciones: 1) Con la implementación actual, los datos deben ser datos diarios o datos horarios.
        # Utilizar datos horarios con horas que faltan datos devolverá resultados erróneos. No sería tan dificil
        # arreglar esto, así que si de verdad te molesta avísame (julien.malard@mail.mcgill.ca)
        # 2) Al momento, solamente se leen documentos .csv de formato INSIVUMEH o con nombres de columnas Y UNIDADES
        # iguales a los utilizados aquí: Fecha, [Hora], Precip (mm), Rad_sol (MJ/m2/día), y Temp (C).

        # Para guardar índices de los datos que faltan
        dic = dict(Precip=[], Rad_sol=[], Temp_máx=[], Temp_mín=[])
        faltan_puntos = dic.copy()
        faltan_porciones = dic.copy()
        # Para guardar los datos de las fechas y horas de los datos
        fechatiempos = fechas = []
        if simismo.ext in documento:  # Si el documento ya es un objeto "diario" guardado
            dic = json.load(documento)
            for f in dic['Fechas']:
                fechas.append(ft.datetime(f[2], f[1], f[0]))
        elif '.csv' in documento:  # Si el documento todavía se encuentra en forma .csv
            # (al momento, sólo lee formato de la INSIVUMEH)
            INSIVUMEH = False

            # Para guardar datos de climar horarios
            precip_hora = temp_hora = rad_sol_hora = []

            with open(documento) as d:
                doc = d.readlines()
            variables = doc[0].split(';')
            conv_var_INSIVUMEH = {'Lluvia': 'Precip', 'R.Global': 'Rad_sol', 'Temp.Ai': 'Temp'}
            # Convertir nombres de variables del formato INSIVUMEH hacia el formato Tikon
            for n, var in enumerate(variables):
                if '[w/m2]' in var:
                    INSIVUMEH = True
                for var_INSI in conv_var_INSIVUMEH:
                    if var_INSI in var:
                        variables[n] = conv_var_INSIVUMEH[var_INSI]

            # Leer los datos
            for i in doc[1:]:
                datos = i.split(';')
                # Leer la fecha y la hora, si aplica
                f = datos[variables.index('Fecha')].split('/')
                fechatiempos.append(ft.datetime(int(f[2]), int(f[1]), int(f[0])))
                if 'Hora' in variables:
                    h = datos[variables.index('Hora')].split(':')
                    fechatiempos[-1] = fechatiempos[-1].replace(hour=int(h[0]), minute=int(h[1]), second=int(h[2]))

                # Convertir los datos vacíos a 'None'
                precip = datos[variables.index('Precip')]
                rad_sol = datos[variables.index('Rad_sol')]
                temp = datos[variables.index('Temp')]
                for var in [precip, rad_sol, temp]:
                    if var == '':
                        var = None

                precip_hora.append(float(precip))
                rad_sol_hora.append(float(rad_sol))
                temp_hora.append(float(temp))

            # Conversiones unidades INSIVUMEH
            if INSIVUMEH:
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
                    rad_sol_cum += rad_sol_hora[n]
                    # Hacer una lista de las temperaturas en el día
                    temp_día.append(temp_hora[n])
                else:
                    dic['Precip'].append(lluvia_cum)
                    lluvia_cum = precip_hora[n+1]
                    dic['Rad_sol'].append(rad_sol_cum)
                    rad_sol_cum = rad_sol_hora[n+1]
                    dic['Temp_mín'].append(min(temp_día))
                    dic['Temp_máx'].append(max(temp_día))
                    temp_día = [temp_hora[n+1]]
                    fechas.append(fechatiempos[n].date())
        else:
            return False

        # Verificar si faltan datos para cada variable
        for var in dic:

            # Verificar si faltan datos puntuales
            f = fecha_inic
            n = 0
            while f <= fecha_fin:
                if f not in fechas or dic[var][n] is None:
                    faltan_puntos[var].append(f)
                f += 1
                n += 1

            # Verificar si faltan grandes extensiones (más de 10 puntos consecutivos) de datos
            faltan_puntos_rev = faltan_puntos[var].copy()
            for n, f in enumerate(faltan_puntos[var]):

                    faltan_porciones = (fecha_inic, min(fechas))
            faltan_puntos[var] = faltan_puntos_rev.copy()


        return faltan_puntos, faltan_porciones, dic


# Esta clase representa el clima de un lugar.
class Clima(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada clima
        simismo.dic_base = dict(Lugar=[], Cód_lugar=[], Lat=[], Long=[], Elev=[], Temp_prom=[], Amp_temp_mens=[],
                                Rad_dia_prom_anual=[], Tdia_máx_prom_anual=[], Tdia_mín_prom_anual=[],
                                Prec_dia_prom_anual=[], Primerdía_sinhelada_prom=[], Prom_dur_heladas=[],
                                Intercept_angstrom=[], Multiplicador_angstrom=[], Alt_med_temp=[], Alt_med_viento=[],
                                Princ_datos_obs=[], Núm_años_obs=[], Mes=[], Rad_prom_mens=[], Tdia_máx_prom_mens=[],
                                Tdia_mín_prom_mens=[], Prec_total_prom_mens=[], Prom_días_prec_mens=[],
                                Horas_sol_dia_prom_mens=[], Intercept_angstrom_mens=[], Multiplicador_angstrom_mens=[],
                                Prom_rad_dia_seco_mens=[], Varia_rad_dia_seco_mens=[], Prom_rad_dia_lluv_mens=[],
                                Varia_rad_dia_lluv_mens=[], Prom_temp_dia_seco_mens=[], Varia_temp_dia_seco_mens=[],
                                Prom_temp_dia_lluv_mens=[], Varia_temp_dia_lluv_mens=[], Varia_temp_dia_min_prom=[],
                                Alpha_distgamma_prec=[], Prob_lluv_después_seco=[])
        super().__init__(*args, **kwargs)  # Esta variable se initializa como
        simismo.ext = "cli"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
