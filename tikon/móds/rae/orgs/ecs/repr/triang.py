import scipy.stats as estad
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs.repr._plntll_ec import EcuaciónReprCoh


class N(Parám):
    nombre = 'n'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=500))


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


class Triang(EcuaciónReprCoh):
    nombre = 'Triang'
    cls_ramas = [N, A, B, C]
    _cls_dist = estad.triang

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(loc=cf['a'], scale=cf['b'], c=cf['c'])
