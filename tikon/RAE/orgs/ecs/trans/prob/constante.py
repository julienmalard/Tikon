from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class Q(Parám):
    nombre = 'q'
    líms = (0, 1)


class Constante(Ecuación):
    nombre = 'Constante'
    _cls_ramas = [Q]
