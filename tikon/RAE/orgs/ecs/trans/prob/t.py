from tikon.ecs.árb_mód import Ecuación, Parám


class K(Parám):
    nombre = 'k'
    líms = (0, None)


class Mu(Parám):
    nombre = 'mu'
    líms = (0, None)


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, None)


class T(Ecuación):
    nombre = 'T'
    cls_ramas = [K, Mu, Sigma]
