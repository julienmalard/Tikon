from tikon.RAE.Planta import Completa
from tikon.RAE.Planta import Hojas
from tikon.RAE.Planta import HojasRaices
from tikon.RAE.Planta import Planta


class Planta(Planta):

    def fijar_densidad(தன், densidad, parte="hoja"):
        return super().fijar_densidad(densidad=densidad, parte=parte)

    def estimar_densidad(தன், rango, certidumbre, parte="hoja"):
        return super().estimar_densidad(rango=rango, certidumbre=certidumbre, parte=parte)

    def externalizar(தன்):
        return super().externalizar()


class Hojas(Hojas):


class HojasRaices(HojasRaices):


class Completa(Completa):
