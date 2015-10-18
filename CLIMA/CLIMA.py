from COSO import Coso
from CLIMA.Estadísticas import *
from CLIMA.Manejo import *
import numpy as np


# Esta clase representa la meteo diaria en un lugar específico.
class Diario(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada suelo
        simismo.dic_base = dict(Lugar=[], País=[], Departamento=[], Municipio=[], Cód_lugar=[], Lat=[], Long=[], 
                                Elev=[], Temp_prom=[], Alt_med_temp=[], Alt_med_viento=[], Amp_temp_mens=[], Fecha=[], 
                                Rad_sol=[], Temp_máx=[], Temp_mín=[], Precip=[], Temp_conden=[], Viento=[], Rad_foto=[],
                                Hum_rel=[])

        super().__init__(*args, **kwargs)  # Esta variable se initializa como Coso
        simismo.ext = "día"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)

        simismo.lugar = simismo.dic['Lugar']
        simismo.país = simismo.dic['País']
        simismo.departamento = simismo.dic['Departamento']
        simismo.municipio = simismo.dic['Municipio']
        simismo.coord = (simismo.dic['Lat'], simismo.dic['Long'])

    def buscar(simismo, fecha_inic, fecha_fin):

        simismo.lugar = simismo.dic['Lugar']
        simismo.país = simismo.dic['País']
        simismo.departamento = simismo.dic['Departamento']
        simismo.municipio = simismo.dic['Municipio']
        simismo.coord = (simismo.dic['Lat'], simismo.dic['Long'])

        encontrado = faltan_pt = faltan_por = faltan = generamos = False
        estación = {}
        estaciones = {}
        dic = dict(Coord=(), Elev='', Datos=dict(Fecha=[], Precip=[], Rad_sol=[], Temp_máx=[], Temp_mín=[]))
        # Buscar en los datos de clima de Python
        with open(os.path.join('CLIMA', 'Estaciones.csv')) as d:
            doc = d.readlines()
        datos = doc[0].split(',')
        col_estación = datos.index('Estación')
        col_long = datos.index('Longitud')
        col_lat = datos.index('Latitud')
        col_alt = datos.index('Altitud')
        col_municipio = datos.index('Municipio')
        
        for lín in doc[1:]:
            datos = lín.split(',')
            estaciones[datos[col_estación]] = dict(Estación=datos[col_estación], Lat=datos[col_lat], 
                                                   Long=datos[col_long], Elev=datos[col_alt],
                                                   Municipio=datos[col_municipio])

        lím_distancia = 10  # acceptamos estaciones adentro de 10 km del lugar de interés
        for i in estaciones:
            # Si hay una estación con el mismo nombre:
            if i['Estación'] == simismo.lugar:
                estación = estaciones[i]
                encontrado = True
                break
            # Sino, si hay una estación con las mismas coordinadas:
            elif i['Lat'] == simismo.coord[0] and i['Long'] == simismo.coord[1]:
                estación = estaciones[i]
                encontrado = True
                break
            # O si hay una estación que no esté muy lejos, lo guardamos al menos que encontremos mejor
            elif dist(simismo.coord, dist(estaciones[i]['Lat'], estaciones[i]['Long'])).km < lím_distancia:
                lím_distancia = dist(estaciones[i]['Lat'], estaciones[i]['Long']).km
                estación = estaciones[i]
                encontrado = True

        if encontrado:
            nombre = estación['Estación']
            directorio = os.path.join('CLIMA', 'DATOS', nombre, '.csv')
            faltan, faltan_pt, faltan_por, dic = cargar_estación(directorio, (estación['Lat'], estación['Long']),
                                                                 estación['Elev'], fecha_inic, fecha_fin)
            if not faltan:
                return  # Si ya lo encontramos sin datos que faltan, parar aquí

        # Si no encontramos la estación, o si faltan datos
        if not encontrado or faltan:
            # Buscar a ver si ya tenemos datos generados para la estación
            for doc_meteogen in os.listdir(os.path.join('CLIMA', 'DATOS', 'Generados')):
                if doc_meteogen.lower() == simismo.lugar.lower() + ".día":
                    faltan, faltan_pt, faltan_por, dic = cargar_estación(doc_meteogen, fecha_inic, fecha_fin)
                    if not faltan:
                        return  # Si ya lo encontramos sin datos que faltan, parar aquí
                    break

        # Si ya encontramos una estación...
        if encontrado:
            # Buscar las estaciones cercanas
            estaciones_cercanas = buscar_cercanas(100, simismo.coord, estaciones)
            for var in dic['Datos']:  # Para cada variable
                if var != 'Fecha' and var != 'Coord':  # Ignorar estas dos llaves del diccionario

                    # Inicializar listas para guardar los datos generados
                    fechas_prededidas_cum = estimaciones_cum = []

                    # Para faltas de datos puntuales y de extensiones de datos
                    for tipo, tipo_f in [('puntual', faltan_pt), ('extensa', faltan_por)]:

                        while len(tipo_f[var]):  # Mientras faltan puntos:

                            # Quitar estaciones sin datos para las fechas de interés
                            estaciones_interés = verificar_fechas(var, estaciones_cercanas, tipo_f[var])

                            # Evaluar estaciones cercanas y calcular la ecuación de estimación
                            a, b, d = eval_estaciones(var, dic, estaciones_interés, tipo)

                            # Aplicar la ecuación generada para las fechas para cuales hay datos en la otra estación
                            fechas_predecidas = [x for x in d['Fecha'] if x in tipo_f[var] and not
                                                 np.isnan(d[var].index(x))]
                            predictores = [x[var] for x in d if d['Fecha'] in fechas_predecidas]
                            estimaciones = [a + x * b for x in predictores]

                            # Guardar los datos en una lista separada
                            estimaciones_cum += estimaciones
                            fechas_prededidas_cum += fechas_predecidas

                            # Quitar las fechas ya estimadas de faltan_pt
                            for fecha in fechas_predecidas:
                                tipo_f[var].pop(tipo_f[var].index(fecha))

                            # Si ninguna estación puede aproximar los puntos que nos faltan, parar
                            if not len(estaciones_interés):
                                break

                    # Guardar las variables estimadas al diccionario
                    if len(fechas_prededidas_cum):
                        generamos = True
                    for f, d in zip(fechas_prededidas_cum, estimaciones_cum):
                        if f in dic['Fecha']:
                            dic['Datos'][var][dic['Fecha'].index(f)] = d
                        else:
                            dic['Datos'][var].append(d)
                            dic['Fecha'].append(f)

        else:  # Si no encontramos una estación, utilizar kriging
            # Buscar las estaciones cercanas
            estaciones_cercanas = buscar_cercanas(30, simismo.coord, estaciones)
            dic = krigear(dic, estaciones_cercanas, fecha_inic, fecha_fin)
            generamos = True

        # Salvar el dic de datos obtuvidos en el diccionario del objeto "diario"
        simismo.dic['Lat'] = dic['Coord'][0]
        simismo.dic['Long'] = dic['Coord'][1]
        simismo.dic['Elev'] = dic['Elev']

        simismo.dic['Fecha'] = [x.strftime('%Y-%m-%d') for x in simismo.dic['Fecha']]
        simismo.dic['Precip'] = dic['Precip']
        simismo.dic['Rad_sol'] = dic['Rad_sol']
        simismo.dic['Temp_máx'] = dic['Temp_máx']
        simismo.dic['Temp_mín'] = dic['Temp_mín']

        # Si generamos datos, salvar el objeto en la base de datos generados de Python
        if generamos:
            simismo.escribir(os.path.join('Proyectos', 'Clima', 'Generado', simismo.lugar, '.día'))


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
