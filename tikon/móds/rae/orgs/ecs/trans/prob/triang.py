import scipy.stats as estad
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónTransCoh


class A(Parám):
    nombre = 'a'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=100))


class B(Parám):
    nombre = 'b'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=100))


class C(Parám):
    nombre = 'c'
    líms = (0, 1)
    unids = None


class Triang(EcuaciónTransCoh):
    nombre = 'Triang'
    cls_ramas = [A, B, C]
    _cls_dist = estad.triang

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(loc=cf['a'], scale=cf['b'], c=cf['c'])
