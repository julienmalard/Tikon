from tikon.ecs.árb_mód import SubcategEc, EcuaciónVacía
from .linear import Linear


class MultTrans(SubcategEc):
    nombre = 'Mult'
    cls_ramas = [EcuaciónVacía, Linear]
    auto = EcuaciónVacía
    _nombre_res = 'Reproducción'
    _eje_cosos = 'etapa'
