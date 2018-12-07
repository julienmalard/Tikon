from tikon.ecs.árb_mód import Ecuación, Parám


class U(Parám):
    nombre = 'u'
    líms = (0, None)


class F(Parám):
    nombre = 'f'
    líms = (0, None)


class Cauchy(Ecuación):
    nombre = 'Cauchy'
    _cls_ramas = [U, F]
