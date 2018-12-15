from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónTrans


class Q(Parám):
    nombre = 'q'
    líms = (0, 1)


class Constante(EcuaciónTrans):
    nombre = 'Constante'
    cls_ramas = [Q]
