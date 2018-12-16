from tikon.ecs.árb_mód import CategEc
from .mult import MultTrans
from .prob import ProbTrans


class EcsTrans(CategEc):
    nombre = 'Transiciones'
    cls_ramas = [ProbTrans, MultTrans]
