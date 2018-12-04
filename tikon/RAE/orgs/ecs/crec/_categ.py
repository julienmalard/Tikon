from tikon.ecs.árb_mód import CategEc
from .ec import EcuaciónCrec
from .modif import ModifCrec


class EcsCrec(CategEc):
    nombre = 'Crecimiento'
    _cls_ramas = [ModifCrec, EcuaciónCrec]
