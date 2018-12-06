from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class N(Parám):
    nombre = 'n'
    líms = (0, None)


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
    _cls_ramas = [N, K, Mu, Sigma]
