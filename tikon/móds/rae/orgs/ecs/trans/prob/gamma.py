import scipy.stats as estad
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónTransCoh


class U(Parám):
    nombre = 'u'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=20))


class A(Parám):
    nombre = 'a'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=10))


class F(Parám):
    nombre = 'f'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=10))


class Gamma(EcuaciónTransCoh):
    nombre = 'Gamma'
    cls_ramas = [U, F, A]
    _cls_dist = estad.gamma

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(loc=cf['u'], scale=cf['f'], a=cf['a'])
