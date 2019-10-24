from tikon.ecs.árb_mód import SubcategEc, EcuaciónVacía
from .lognorm_temp import LogNormTemp
from .ninguna import Ninguna


class ModifCrec(SubcategEc):
    nombre = 'Modif'
    cls_ramas = [EcuaciónVacía, Ninguna, LogNormTemp]
    _nombre_res = CREC
    _eje_cosos = EJE_ETAPA
