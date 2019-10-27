import scipy.stats as estad
from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónTransCoh


class U(Parám):
    nombre = 'u'
    líms = (0, None)
    unids = None


class F(Parám):
    nombre = 'f'
    líms = (0, None)
    unids = None


class Cauchy(EcuaciónTransCoh):
    nombre = 'Cauchy'
    cls_ramas = [U, F]
    _cls_dist = estad.cauchy

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(loc=cf['u'], scale=cf['f'])
