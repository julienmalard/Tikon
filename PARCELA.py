from COSO import Coso
from CULTIVO.CULTIVO import Cultivo
from CULTIVO.SUELO import Suelo
from PLAGAS.PLAGAS import Red
from CULTIVO.VARIEDAD import Variedad
import os


# Una parcela se refiere a una unidad de tierra homógena en sus suelo, cultivo(s)
# y otras propiedades
class Parcela(Coso):
    def __init__(self, suelos_común, variedades_común, redes_común, *args, **kwargs):
        self.dic_base = {"Suelo": "", "Variedad": "", "Meteo": "", "RedAE": "", "Long": (), "Lat": ()}
        self.suelos_común = suelos_común
        self.variedades_común = variedades_común
        self.redes_común = redes_común
        super().__init__(*args, **kwargs)
        self.ext = "par"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        # Crear la carpeta para la parcela:
        if (not self.variedades_común) or (not self.suelos_común):
            if not os.path.exists(os.path.splitext(self.documento)[0]):  # splitext quita la extensión
                os.makedirs(os.path.splitext(self.documento)[0])

        # Dar el directorio apropiado a la variedad de cultivo y el suelo utilizados para esta parcela
        if self.variedades_común:  # Si la parcela comparte variedades con otros proyectos (para calibración)
            carpeta_variedad = "Parcelas" + "\\" + "Variedades"
        else:  # Si la parcela tiene sus variedades individuales (para calibración)
            carpeta_variedad = self.carpeta
        if self.suelos_común:  # Si la parcela comparte suelo con otros proyectos (para calibración)
            carpeta_suelo = "Parcelas" + "\\" + "Suelos"
        else:  # Si la parcela tiene sus suelos individuales (para calibración)
            carpeta_suelo = self.carpeta
        if self.redes_común:
            carpeta_redes = "Parcelas" + "\\" + "Redes"
        else:  # Si la parcela tiene sus suelos individuales (para calibración)
            carpeta_redes = self.carpeta

        # Definir el cultivo y la red agroecológica
        self.red = Red(nombre=self.dic["RedAE"], carpeta=carpeta_redes, reinit=self.reinit)
        self.variedad = Variedad(nombre=self.dic["Variedad"], carpeta=carpeta_variedad,
                                 reinit=self.reinit)
        self.suelo = Suelo(nombre=self.dic["Variedad"], carpeta=carpeta_suelo, reinit=self.reinit)
        self.cultivo = Cultivo(nombre=self.dic["Cultivo"], variedad=self.variedad,
                               suelo=self.dic["Suelo"], meteo=self.dic["Meteo"],
                               fecha_siembra=self.dic["Fecha_siembra"])

        # Poner a 0 los valores iniciales del cultivo y de las plagas
        self.estado_cultivo = {}
        self.daño_plagas = {}
        self.plagas = {}

    # Esta función inicializa los modelos para la parcela
    def ejec(self, tiempo_init):
        # Una carpeta para guardar los resultados del modelo de cultivos
        carpeta_egr = os.path.join(self.carpeta,"egresos_mod_cul")
        # El modelo del cultivo define el tiempo para la simulación:
        self.cultivo.ejec(tiempo_init, carpeta_egr=carpeta_egr)
        # El modelo de plagas sigue mientras hay un modelo de cultivo activo
        self.red = eval(self.dic["RedAE"])

    def incr(self, paso):
        if self.cultivo.proceso.poll is None:
            self.estado_cultivo = self.cultivo.incr(paso, self.daño_plagas)
            self.daño_plagas, self.plagas = self.red.incr(self.estado_cultivo, paso)
        else:
            return "Modelo de cultivo terminado."
