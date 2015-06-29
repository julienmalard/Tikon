from COSO import Coso
from CULTIVO.CULTIVO import Cultivo
from PLAGAS.PLAGAS import Red


# Una parcela se refiere a una unidad de tierra homógena en sus suelo, cultivo(s)
# y otras propiedades
class Parcela(Coso):
    def __init__(self, *args, **kwargs):
        self.dic_base = {"Suelo": "", "Cultivo": "", "Meteo": ""}
        super().__init__(*args, **kwargs)
        self.ext = "par"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        #  Definir el cultivo y la red agroecológica
        self.cultivo = Cultivo(self.dic["Cultivo"], self.dic["Variedad"],
                               self.dic["Suelo"], self.dic["Meteo"])
        self.red = Red()

        # Poner a 0 los valores iniciales del cultivo y de las plagas
        self.estado_cultivo = {}
        self.daño_plagas = {}

    def ejec(self, tiempo_init):
        self.cultivo.ejec(tiempo_init)  # El modelo del cultivo define el tiempo para la simulación
        self.plagas.ejec()  # El modelo de plagas sigue mientras hay un modelo de cultivo activo

    def incr(self, paso):
        self.estado_cultivo = self.cultivo.incr(paso, self.daño_plagas)
        self.daño_plagas = self.red.incr(self.estado_cultivo, paso)
