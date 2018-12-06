from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class Mu(Parám):
    nombre = 'mu'
    líms = (0, None)


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, None)


class Normal(Ecuación):
    nombre = 'Normal'
    _cls_ramas = [Mu, Sigma]
