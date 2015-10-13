import os
from COSO import Coso


# Esta clase representa la meteo diaria en un lugar específico.
class Diario(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada suelo
        simismo.dic_base = dict(Lugar=[], Cód_lugar=[], Lat=[], Long=[], Elev=[], Temp_prom=[], Alt_med_temp=[],
                                Alt_med_viento=[], Amp_temp_mens=[], Fecha=[], Rad_sol=[], Temp_máx=[], Temp_mín=[],
                                Precip=[], Temp_conden=[], Viento=[], Rad_foto=[])

        super().__init__(*args, **kwargs)  # Esta variable se initializa como Coso
        simismo.ext = "día"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)

        simismo.lugar = simismo.dic['Lugar']
        simismo.coord = (simismo.dic['Lat'], simismo.dic['Long'])

    def buscar(simismo, fecha_inic, fecha_fin):

        directorio = None
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
                elif datos_estación[col_municipio] == simismo.lugar and ():
                    encontrado = True
                    break
            if encontrado:
                estación = datos_estación[col_estación]
                directorio = os.path.join('Proyectos', 'Clima', estación, '.csv')
                faltan_pt, faltan_por = simismo.leer_estación(directorio, fecha_inic, fecha_fin)
                if not (faltan_pt and faltan_por):
                    return  # Si ya lo encontramos sin datos que faltan, parar aquí

        # Si no encontramos la estación, o si faltan datos
        if not encontrado or (faltan_pt and faltan_por):
            # Buscar a ver si ya tenemos datos generados para la estación
            for doc_meteogen in os.listdir(os.path.join('Proyectos', 'Clima', 'Generados')):
                if doc_meteogen.lower().endswith(".día") and simismo.lugar.lower() in doc_meteogen.lower():
                    encontrado = True
                    directorio = os.path.join('Proyectos', 'Clima', 'Generados', doc_meteogen)
                    faltan_pt, faltan_por = simismo.leer_estación(directorio, fecha_inic, fecha_fin)
                    if not (faltan_pt and faltan_por):
                        return  # Si ya lo encontramos sin datos que faltan, parar aquí
                    break

        if encontrado:
            if faltan_pt:  # Si faltan puntos puntuales:
                generamos = True  # Marcar que hemos generado datos
                pass
                # todo: Análisis Bahaa Khalil rellenar puntos
            if faltan_por:  # Si faltan grandes pedazos de datos
                generamos = True # Marcar que hemos generado datos
                pass
                # todo: Análisis Bahaa Khalil extensión de datos

        # Si no encontramos una estación o no logramos generar los datos necesarios, utilizar kriging
        if not encontrado or faltan_pt or faltan_por:
            pass
            # TODO: kringing

        # Si generamos datos, salvar el objeto en la base de datos generados de Python
        if generamos:
            simismo.escribir(os.path.join('Proyectos', 'Clima', 'Generado', simismo.lugar, '.día'))

    # Una función para leer los datos de clima de un documento especificado
    def leer_estación(simismo, directorio, fecha_inic, fecha_fin):
        faltan_puntos, faltan_porciones = False
        with open(directorio) as d:
            datos = d.readlines()
            # Leer la fecha y la hora, si aplica

            # Leer los variables meteorológicos

            # Sumar datos horarios por por fecha, si aplicable
        # todo
        return faltan_puntos, faltan_porciones


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
