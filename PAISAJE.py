import os
import numpy as np
import datetime as ft
from geopy.distance import vincenty as dist

from COSO import Coso
from PARCELA import Parcela
from CULTIVO.SUELO import Suelo
from CULTIVO.VARIEDAD import Variedad
from CLIMA.CLIMA import Diario
from RAE.REDES import Red


class Paisaje(Coso):
    def __init__(símismo, nombre, datos=None, variedades_común=True, suelos_común=True, redes_común=True, fecha_inic="",
                 fecha_fin="", reinic=None):
        dic = {'Directorio': '', 'Nombre': '', 'fecha_inic': fecha_inic, 'fecha_fin': fecha_fin,
               'variedades_común': variedades_común, 'suelos_común': suelos_común, 'redes_común': redes_común,
               'Parcelas': dict(Nombre=[], Long=[], Lat=[], Dilim=[]),
               'RedAE': ""
               }
        if reinic is None:
            reinic = datos is None  # si se dieron nuevos datos, reinicializamos el modelo

        # Llamar los métodos de las clase Coso
        super().__init__(nombre=nombre, ext='pais', dic=dic, directorio='Personales\\Paisajes', reinic=reinic)
        símismo.dic['Directorio'] = símismo.directorio
        símismo.dic['Nombre'] = símismo.nombre

        símismo.datos_crud = {}  # Un diccionario con los datos crudos de las parcelas
        símismo.parcelas = {}  # Un diccionario de las parcelas del paisaje
        símismo.suelos = {}
        símismo.meteos = {}
        símismo.variedades = {}
        símismo.resultados = {}  # Un diccionario para guardar los resultados de la simulación
        símismo.distancias = {}  # Par guardar las distancias entre las parcelas

        símismo.red = None

        # Inicializar el paisaje
        símismo.inic(datos)

    # Esta función toma datos de parcelas (listas) del paisaje y dinámicamente cree objetos Python para cada uno.
    def inic(símismo, datos):
        if datos:  # Si se especificaron datos, leerlos
            datos_crudos = símismo.leer_documento(datos)
            for núm, nombre in enumerate(datos_crudos['Parcela']):
                nueva_parcela = Parcela(nombre=nombre, directorio=símismo.directorio,
                                        suelos_común=símismo.dic['suelos_común'],
                                        variedades_común=símismo.dic['variedades_común'],
                                        redes_común=símismo.dic['redes_común'])

                def leer_vars(obj):
                    for var in obj:
                        if type(var) is dict:
                            leer_vars(obj[var])
                        if var in datos_crudos:
                            try:
                                valor = float(datos_crudos[var][núm])
                            except ValueError:
                                valor = datos_crudos[var][núm]
                            obj[var] = valor

                leer_vars(nueva_parcela.dic)

                símismo.parcelas[nombre] = nueva_parcela

        if símismo.dic['redes_común']:  # Si compartemos redes, buscar la red en el lugar común
            símismo.red = Red(nombre=símismo.dic['RedAE'])
        else:  # Si no compartemos, buscarla en el directorio del paisaje actual
            if os.path.isfile(os.path.join(símismo.directorio, símismo.nombre + '.red')):
                símismo.red = Red(nombre=símismo.dic['RedAE'])
            else:  # Si no lo encontramos allí, hacer una copia local de la versión en el lugar común
                dirección = os.path.join('Proyectos', 'Personales', 'Redes', símismo.nombre + '.red')
                if os.path.isfile(dirección):
                    with open(dirección) as d:
                        doc = d.readlines()
                    with open(os.path.join(símismo.directorio, símismo.nombre + '.red'), 'w') as d:
                        d.write(doc)
                else:
                    print('No se encontró la red agroecológica %s.' % (símismo.nombre + '.red'))

        # Poner los suelos, variedades, y redes a la parcela
        for itema in símismo.parcelas.items():
            parcela = itema[1]  # Sacar el objeto representando la parcela
            if símismo.dic['suelos_común']:
                # Si todavía no hemos creado un objeto para el suelo en cuestión:
                if parcela.dic['Suelo'] not in símismo.suelos:
                    símismo.suelos[parcela.dic['Suelo']] = Suelo(nombre=parcela.dic['Suelo'],
                                                                 directorio=símismo.directorio)

                # Establecer una referencia entre el suelo apropiade del diccionario de suelos y el suelo de la parcela
                parcela.suelo = símismo.suelos[parcela.dic['Suelo']]

            # Las variedades
            if símismo.dic['variedades_común']:
                # Si todavía no hemos creado un objeto para la variedad en cuestión:
                if parcela.dic['Variedad'] not in símismo.variedades:
                    símismo.variedades[parcela.dic['Variedad']] = Variedad(nombre=parcela.dic['Variedad'],
                                                                           directorio=símismo.directorio)

                # Establecer una referencia entre la variedad del diccionario de variedades y la variedad de la parcela
                parcela.variedad = símismo.variedades[parcela.dic['Variedad']]

            # El clima
            meteo_temp = Diario(coord=(parcela.dic['Lat'], parcela.dic['Long']))
            meteo_temp.buscar(símismo.dic['fecha_inic'], símismo.dic['fecha_fin'])
            # Si todavía no hemos creado un objeto para la meteorología en cuestión:
            if meteo_temp.nombre not in símismo.meteos:
                símismo.meteos[meteo_temp.nombre] = Diario(nombre=parcela.dic['Variedad'])
            parcela.meteo = símismo.meteos[meteo_temp.nombre]

            # Las redes agroecológicas
            parcela.red = símismo.red

            # Calcular distancias entre parcelas
            for otro_itema in símismo.parcelas.items():
                otra_parcela = otro_itema[1]
                símismo.distancias[itema[0]][otro_itema[1]] = dist((parcela.dic["Lat"], parcela.dic["Long"]),
                                                                   (otra_parcela.dic["Lat"], otra_parcela.dic["Long"]))

    # Esta función lee los datos de parcelas desde un documento .csv y los guarda en unas listas
    @staticmethod
    def leer_documento(documento):
        try:
            with open(documento, mode="r") as d:
                doc = d.readlines()
        except IOError:
            return u'El documento {0:s} no se pudo abrir.'.format(documento)

        datos_crud = {}
        variables = doc[0].replace(';', ',').split(',')
        for var in variables:
            datos_crud[var] = []
        for num_lín, línea in enumerate(doc[1:]):
            if len(línea):
                valores = línea.replace(';', ',').split(',')
                for posición, variable in enumerate(variables):
                    datos_crud[variable].append(valores[posición].replace('\n', ''))
        return datos_crud

    def simul(símismo, fecha_init, tiempo_simul, paso):
        fecha = fecha_init
        for parcela in símismo.parcelas:
            parcela.ejec(fecha_init)
        for tiempo in range(0, tiempo_simul):
            for parcela in símismo.parcelas:
                # Si el modelo de cultivo se terminó:
                if parcela.cultivo.poll is not None:
                    # TODO: poner código para reinicializar la parcela
                    pass
                # Incrementar la parcela
                fecha.incr(paso)  # Incrementar el tiempo
                parcela.incr(paso)

                # Controlar la migración de plagas entre parcelas:
                # Calcular la imigración y emigración para hoy
                for otra_parcela in símismo.parcelas:
                    if parcela is not otra_parcela:
                        for insecto in parcela.red.insectos:
                            # const_migr podría modificarse para ser una funcción de las dos parcelas en cuestión.
                            distancia = parcela.dist[otra_parcela]
                            const_migr = parcela.RedAE.insecto.dic["const_migr"]
                            migración = parcela.plagas[insecto] * const_migr * (1 / distancia) ** 2
                            parcela.emigración[insecto] += migración
                            otra_parcela.imigración[insecto] += migración

            # Implementar las migraciones. La implementación de las migraciones después de calcular todas las
            # migraciones evita problemas de migraciones círculas entre parcelas.
            for parcela in símismo.parcelas:
                for insecto in parcela.red.insectos:
                    parcela.red.insectos[insecto] -= parcela.emigración[insecto]
                    parcela.red.insectos[insecto] += parcela.imigración[insecto]
                    parcela.resultados[insecto]["Emigración"].append(parcela.emigración[insecto])
                    parcela.resultados[insecto]["Imigración"].append(parcela.imigración[insecto])
                    parcela.insectos = parcela.red.insectos  # Salvar los datos en el diccionario local de la parcela

            # Guardar el tiempo
            símismo.resultados["Día"].append(fecha.díaaño)

        # Guardar resultados finales
        for parcela in símismo.parcelas:
            símismo.resultados[parcela] = parcela.resultados
