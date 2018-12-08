from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from .asimp_hum import AsimptóticoHumedad
from .constante import Constante
from .lognorm_temp import LogNormTemp
from .sig_temp import SigmoidalTemperatura


class EcuaciónMuerte(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [EcuaciónVacía, Constante, LogNormTemp, AsimptóticoHumedad, SigmoidalTemperatura]
    auto = Constante


class EcsMuerte(CategEc):
    nombre = 'Muertes'
    cls_ramas = [EcuaciónMuerte]
