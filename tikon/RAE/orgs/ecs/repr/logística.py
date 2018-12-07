from tikon.ecs.árb_mód import Ecuación, Parám


class N(Parám):
    nombre = 'n'
    líms = (0, None)


class U(Parám):
    nombre = 'u'
    líms = (0, None)


class F(Parám):
    nombre = 'f'
    líms = (0, None)


class Logística(Ecuación):
    nombre = 'Logística'
    _cls_ramas = [N, U, F]
