from tikon.ecs.árb_mód import Ecuación, Parám


class N(Parám):
    nombre = 'n'
    líms = (0, None)


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
    cls_ramas = [N, U, F, A]
