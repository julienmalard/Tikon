import scipy.stats as estad
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs.repr._plntll_ec import EcuaciónReprCoh


class N(Parám):
    nombre = 'n'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=500))


class U(Parám):
    nombre = 'u'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=100))


class F(Parám):
    nombre = 'f'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=10))


class Cauchy(EcuaciónReprCoh):
    nombre = 'Cauchy'
    cls_ramas = [N, U, F]
    _cls_dist = estad.cauchy

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(loc=cf['u'], scale=cf['f'])
