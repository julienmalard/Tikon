from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class N(Parám):
    nombre = 'n'
    líms = (0, None)


class Constante(Ecuación):
    nombre = 'Constante'
    _cls_ramas = [N]
