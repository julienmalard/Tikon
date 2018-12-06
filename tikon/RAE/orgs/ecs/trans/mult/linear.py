from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class Linear(Ecuación):
    nombre = 'Linear'
    _cls_ramas = [A]
