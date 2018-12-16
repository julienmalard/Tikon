from tikon.ecs.árb_mód import Ecuación, Parám


class N(Parám):
    nombre = 'n'
    líms = (0, None)


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class B(Parám):
    nombre = 'b'
    líms = (0, None)


class C(Parám):
    nombre = 'c'
    líms = (0, None)


class Triang(Ecuación):
    nombre = 'Triang'
    cls_ramas = [N, A, B, C]
