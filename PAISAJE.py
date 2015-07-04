from COSO import Coso
from PARCELA import Parcela
import math, os, shutil


class Paisaje(Coso):
    def __init__(self, parcelas_común=False, variedades_común=True, suelos_común=True, redes_común=True,
                 *args, **kwargs):
        self.dic_base = {"Parcelas": [], "Cultivos": [], "Long": [], "Lat": [],
                         "Fechas_siembra": [], "Suelos": [], "RedAE": (), "Meteo": ()}
        self.ext = "pasj"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        super().__init__(*args, **kwargs)
        self.parcelas_común = parcelas_común
        self.variedades_común = variedades_común
        self.suelos_común = suelos_común
        self.redes_común = redes_común
        self.parcelas = {}
        self.resultados = {}
        self.init()
        # Información de distancia entre parcelas
        for parcela in self.dic["Parcelas"]:
            for otra_parcela in self.dic["Parcelas"]:
                parcela.dist[otra_parcela] = math.sqrt((parcela.dic["Long"] - otra_parcela.dic["Long"]) ** 2 -
                                                       (parcela.dic["Lat"] - otra_parcela.dic["Lat"]) ** 2)

    # Esta función toma el diccionario (listas) del paisaje y dinámicamente cree objetos Python para cada uno.
    def init(self):
        # Crear los directorios para el proyecto
        if not os.path.exists(self.documento):
            os.makedirs(self.documento)
        if self.parcelas_común:  # Si el paisaje comparte parcelas con otros proyectos (para la calibración)
            carpeta_parcelas = "Parcelas"
        else:  # Si el paisaje tiene sus parcelas individuales (para la calibración)
            carpeta_parcelas = self.carpeta
        # Crear los objectos de parcelas para cada parcela en el paisaje
        for num_parcela, parcela in enumerate(self.dic["Parcelas"]):
            self.parcelas[parcela] = Parcela(parcela, carpeta=os.path.join(carpeta_parcelas, parcela),
                                             reinit=self.reinit, redes_común = self.redes_común,
                                             suelos_común = self.suelos_común, variedades_común = self.variedades_común,
                                             dic={"Suelo": self.dic["Suelos"][num_parcela],
                                                  "Cultivo": self.dic["Cultivos"][num_parcela],
                                                  "Meteo": self.dic["Meteo"],
                                                  "RedAE": self.dic["RedAE"],
                                                  "Long": self.dic["Long"][num_parcela],
                                                  "Lat": self.dic["Lat"][num_parcela]},
                                             )

    # Esta función lee los datos de parcelas desde un documento .csv y los guarda en el diccionario del paisaje
    def leer_documento(self, documento):
        try:
            with open(documento, mode="r") as d:
                for num_lín, línea in enumerate(d):
                    if num_lín == 0:
                        variables = línea.split(',')
                    else:
                        if len(línea):
                            valores = línea.split(',')
                            for posición, variable in enumerate(variables):
                                if variable in self.dic:  # Si el variable corresponde a un variable en el diccionario
                                    self.dic[variable][num_lín] = valores[posición].replace("\n", "")
        except IOError:
            return "Carpeta " + documento + " no se pudo abrir."

    def simul(self, tiempo_init, tiempo_fin, paso):
        for parcela in self.dic["Parcelas"]:
            parcela.ejec(tiempo_init)
        for día in range(tiempo_init, tiempo_fin):
            for parcela in self.dic["Parcelas"]:
                if parcela.cultivo.poll is not None:  # Si el modelo de cultivo se terminó:
                    # TODO: poner código para reinicializar la parcela
                    pass
                parcela.incr(paso)
                for otra_parcela in self.dic["Parcelas"]:
                    if parcela is not otra_parcela:
                        for insecto in parcela.plagas:
                            # const_migr podría modificarse para ser una funcción de las dos parcelas en cuestión.
                            dist = parcela.dist[otra_parcela]
                            const_migr = parcela.RedAE.insecto.dic["const_migr"]
                            migración = parcela.plagas[insecto] * const_migr * (1/dist)**2
                            otra_parcela.plagas[insecto] += migración
                            parcela.plagas -= migración
            self.resultados["Día"] = día
            self.resultados[""]
