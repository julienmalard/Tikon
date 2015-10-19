import os
import datetime as ft
from geopy.distance import vincenty as dist

from COSO import Coso
from PARCELA import Parcela


class Paisaje(Coso):
    def __init__(símismo, variedades_común=True, suelos_común=True, redes_común=True, fecha_inic="", fecha_fin=""):
        símismo.dic_base = {'Directorio': '', 'fecha_init': fecha_inic, 'fecha_fin': fecha_fin,
                            'variedades_común': variedades_común, 'suelos_común': suelos_común,
                            'redes_común': redes_común,
                            'Parcelas': dict(Nombre=[], Long=[], Lat=[], Dilim=[]),
                            'RedAE': ""
                            }
        símismo.ext = "pasj"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        super().__init__(ext='pais')
        símismo.parcelas = {}
        símismo.resultados = {}
        símismo.init()

    # Esta función lee los datos de parcelas desde un documento .csv y los guarda en el diccionario del paisaje
    def leer_documento(símismo, documento):
        try:
            with open(documento, mode="r") as d:
                doc = d.readlines()
        except IOError:
            return u'El documento {0:s} no se pudo abrir.'.format(documento)

        variables = doc[0].split(',')
        for num_lín, línea in enumerate(doc[1:]):
            if len(línea):
                valores = línea.split(',')
                for posición, variable in enumerate(variables):
                    # Si el variable corresponde a un variable en el diccionario
                    if variable in símismo.dic:
                        símismo.dic[variable][num_lín] = valores[posición].replace('\n', '')

    # Esta función toma el diccionario (listas) del paisaje y dinámicamente cree objetos Python para cada uno.
    def init(símismo):
        # Crear los directorios para el proyecto
        if not os.path.exists(símismo.documento):
            os.makedirs(símismo.documento)

        else:  # Si el paisaje tiene sus parcelas individuales (para la calibración)
            carpeta_parcelas = símismo.carpeta
        # Crear los objectos de parcelas para cada parcela en el paisaje
        for num_parcela, parcela in enumerate(símismo.dic["Parcelas"]):
            símismo.parcelas[parcela] = \
                Parcela(nombre=parcela, carpeta=os.path.join(carpeta_parcelas, parcela),
                        reinit=símismo.reinit, redes_común=símismo.redes_común,
                        suelos_común=símismo.suelos_común, variedades_común=símismo.variedades_común,
                        dic={"Suelo": símismo.dic["Suelos"][num_parcela],
                             "Cultivo": símismo.dic["Cultivos"][num_parcela],
                             "Variedad": símismo.dic["Variedades"][num_parcela], "Meteo": símismo.dic["Meteo"],
                             "RedAE": símismo.dic["RedAE"], "Long": símismo.dic["Long"][num_parcela],
                             "Lat": símismo.dic["Lat"][num_parcela]}
                        )

        # Información de distancia entre parcelas
        for parcela in símismo.parcelas:
            for otra_parcela in símismo.parcelas:
                parcela.dist[otra_parcela] = dist((parcela.dic["Lat"], parcela.dic["Long"]),
                                                  (otra_parcela.dic["Lat"] , otra_parcela.dic["Long"]))


    def simul(símismo, fecha_init, tiempo_simul, paso):  # fecha_init tiene que ser del formato AAAAMMDD
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
                            dist = parcela.dist[otra_parcela]
                            const_migr = parcela.RedAE.insecto.dic["const_migr"]
                            migración = parcela.plagas[insecto] * const_migr * (1 / dist) ** 2
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
