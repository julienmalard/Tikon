import scipy.stats as estad
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs.trans.prob._plntll_ec import EcuaciónTransCoh


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


class Logística(EcuaciónTransCoh):
    nombre = 'Logística'
    cls_ramas = [U, F]
    _cls_dist = estad.logistic

    def _prms_scipy(símismo):
        return dict(loc=símismo.cf['u'], scale=símismo.cf['f'])
