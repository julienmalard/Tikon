from tikon.ecs.árb_mód import SubcategEc, EcuaciónVacía
from .ninguna import Ninguna
from .lognorm_temp import LogNormTemp


class ModifCrec(SubcategEc):
    nombre = 'Modif'
    cls_ramas = [EcuaciónVacía, Ninguna, LogNormTemp]
