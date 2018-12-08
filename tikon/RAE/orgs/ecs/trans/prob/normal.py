from tikon.ecs.árb_mód import Ecuación, Parám


class Mu(Parám):
    nombre = 'mu'
    líms = (0, None)


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, None)


class Normal(Ecuación):
    nombre = 'Normal'
    cls_ramas = [Mu, Sigma]
