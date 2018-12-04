from tikon.ecs.árb_mód import SubcategEc, EcuaciónVacía
from .const import Constante
from .expon import Expon
from .logíst import Logíst
from .logíst_depred import LogístDepred
from .logíst_presa import LogístPresa


class EcuaciónCrec(SubcategEc):
    nombre = 'Ecuación'
    _cls_ramas = [EcuaciónVacía, Expon, Logíst, LogístPresa, LogístDepred, Constante]
    auto = EcuaciónVacía
