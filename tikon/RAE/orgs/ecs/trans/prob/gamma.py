from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class U(Parám):
    nombre = 'u'
    líms = (0, None)


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class F(Parám):
    nombre = 'f'
    líms = (0, None)


class Gamma(Ecuación):
    nombre = 'Gamma'
    _cls_ramas = [U, F, A]
