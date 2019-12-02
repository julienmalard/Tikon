import scipy.stats as estad
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónReprCoh


class N(Parám):
    nombre = 'n'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=500))


class Mu(Parám):
    nombre = 'mu'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=100))


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=10))


class Normal(EcuaciónReprCoh):
    """
    Distribución normal de reproductividad a través de la vida de la etapa.
    """
    nombre = 'Normal'
    cls_ramas = [N, Mu, Sigma]
    _cls_dist = estad.norm

    def _prms_scipy(símismo):
        return dict(loc=símismo.cf['mu'], scale=símismo.cf['sigma'])
