import scipy.stats as estad
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs.repr._plntll_ec import EcuaciónReprCoh


class N(Parám):
    nombre = 'n'
    líms = (0, None)
    unids = None


class U(Parám):
    nombre = 'u'
    líms = (0, None)
    unids = None


class A(Parám):
    nombre = 'a'
    líms = (0, None)
    unids = None


class F(Parám):
    nombre = 'f'
    líms = (0, None)
    unids = None


class Gamma(EcuaciónReprCoh):
    nombre = 'Gamma'
    cls_ramas = [N, U, F, A]
    _cls_dist = estad.gamma

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(a=cf['a'], loc=cf['u'], scale=cf['f'])
