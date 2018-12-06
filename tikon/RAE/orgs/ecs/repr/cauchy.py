from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class N(Parám):
    nombre = 'n'
    líms = (0, None)


class U(Parám):
    nombre = 'u'
    líms = (0, None)


class F(Parám):
    nombre = 'f'
    líms = (0, None)


class Cauchy(Ecuación):
    nombre = 'Cauchy'
    _cls_ramas = [N, U, F]
