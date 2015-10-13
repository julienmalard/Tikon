from COSO import Coso
from PARCELA import Parcela
import datetime as fecha
import math, os, shutil


class Paisaje(Coso):
    def __init__(simismo, parcelas_común=False, variedades_común=True, suelos_común=True, redes_común=True,
                 *args, **kwargs):
        simismo.dic_base = {"Parcelas": [], "Cultivos": [], "Variedades": [], "Long": [], "Lat": [],
                         "Fechas_siembra": [], "Suelos": [], "RedAE": (), "Meteo": ()}
        simismo.ext = "pasj"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        super().__init__(*args, **kwargs)
        simismo.parcelas_común = parcelas_común
        simismo.variedades_común = variedades_común
        simismo.suelos_común = suelos_común
        simismo.redes_común = redes_común
        simismo.parcelas = {}
        simismo.resultados = {}
        simismo.init()
        # Información de distancia entre parcelas
        for parcela in simismo.dic["Parcelas"]:
            for otra_parcela in simismo.dic["Parcelas"]:
                parcela.dist[otra_parcela] = math.sqrt((parcela.dic["Long"] - otra_parcela.dic["Long"]) ** 2 -
                                                       (parcela.dic["Lat"] - otra_parcela.dic["Lat"]) ** 2)

    # Esta función lee los datos de parcelas desde un documento .csv y los guarda en el diccionario del paisaje
    def leer_documento(simismo, documento):
        try:
            with open(documento, mode="r") as d:
                for num_lín, línea in enumerate(d):
                    if num_lín == 0:
                        variables = línea.split(',')
                    else:
                        if len(línea):
                            valores = línea.split(',')
                            for posición, variable in enumerate(variables):
                                if variable in simismo.dic:  # Si el variable corresponde a un variable en el diccionario
                                    simismo.dic[variable][num_lín] = valores[posición].replace("\n", "")
        except IOError:
            return "Carpeta " + documento + " no se pudo abrir."

    # Esta función toma el diccionario (listas) del paisaje y dinámicamente cree objetos Python para cada uno.
    def init(simismo):
        # Crear los directorios para el proyecto
        if not os.path.exists(simismo.documento):
            os.makedirs(simismo.documento)
        if simismo.parcelas_común:  # Si el paisaje comparte parcelas con otros proyectos (para la calibración)
            carpeta_parcelas = "Parcelas"
        else:  # Si el paisaje tiene sus parcelas individuales (para la calibración)
            carpeta_parcelas = simismo.carpeta
        # Crear los objectos de parcelas para cada parcela en el paisaje
        for num_parcela, parcela in enumerate(simismo.dic["Parcelas"]):
            simismo.parcelas[parcela] = Parcela(nombre=parcela, carpeta=os.path.join(carpeta_parcelas, parcela),
                                             reinit=simismo.reinit, redes_común=simismo.redes_común,
                                             suelos_común=simismo.suelos_común, variedades_común=simismo.variedades_común,
                                             dic={"Suelo": simismo.dic["Suelos"][num_parcela],
                                                  "Cultivo": simismo.dic["Cultivos"][num_parcela],
                                                  "Variedad": simismo.dic["Variedades"][num_parcela],
                                                  "Meteo": simismo.dic["Meteo"],
                                                  "RedAE": simismo.dic["RedAE"],
                                                  "Long": simismo.dic["Long"][num_parcela],
                                                  "Lat": simismo.dic["Lat"][num_parcela]},
                                             )

    def simul(simismo, fecha_init, tiempo_simul, paso):  # fecha_init tiene que ser del formato AAAAMMDD
        fecha = Fechas.Fecha(díaaño=fecha_init)
        for parcela in simismo.parcelas:
            parcela.ejec(fecha_init)
        for tiempo in range(0, tiempo_simul):
            for parcela in simismo.parcelas:
                # Si el modelo de cultivo se terminó:
                if parcela.cultivo.poll is not None:
                    # TODO: poner código para reinicializar la parcela
                    pass
                # Incrementar la parcela
                fecha.incr(paso)  # Incrementar el tiempo
                parcela.incr(paso)

                # Controlar la migración de plagas entre parcelas:
                # Calcular la imigración y emigración para hoy
                for otra_parcela in simismo.parcelas:
                    if parcela is not otra_parcela:
                        for insecto in parcela.red.insectos:
                            # const_migr podría modificarse para ser una funcción de las dos parcelas en cuestión.
                            dist = parcela.dist[otra_parcela]
                            const_migr = parcela.RedAE.insecto.dic["const_migr"]
                            migración = parcela.plagas[insecto] * const_migr * (1/dist)**2
                            parcela.emigración[insecto] += migración
                            otra_parcela.imigración[insecto] += migración

            # Implementar las migraciones. La implementación de las migraciones después de calcular todas las
            # migraciones evita problemas de migraciones círculas entre parcelas.
            for parcela in simismo.parcelas:
                for insecto in parcela.red.insectos:
                    parcela.red.insectos[insecto] -= parcela.emigración[insecto]
                    parcela.red.insectos[insecto] += parcela.imigración[insecto]
                    parcela.resultados[insecto]["Emigración"].append(parcela.emigración[insecto])
                    parcela.resultados[insecto]["Imigración"].append(parcela.imigración[insecto])
                    parcela.insectos = parcela.red.insectos  # Salvar los datos en el diccionario local de la parcela

            # Guardar el tiempo
            simismo.resultados["Día"].append(fecha.díaaño)

        # Guardar resultados finales
        for parcela in simismo.parcelas:
            simismo.resultados[parcela] = parcela.resultados
