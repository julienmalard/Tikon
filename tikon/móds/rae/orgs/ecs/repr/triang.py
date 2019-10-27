import scipy.stats as estad
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs.repr._plntll_ec import EcuaciónReprCoh


class N(Parám):
    nombre = 'n'
    líms = (0, None)
    unids = None


class A(Parám):
    nombre = 'a'
    líms = (0, None)
    unids = None


class U(Parám):
    nombre = 'u'
    líms = (0, None)
    unids = None


class F(Parám):
    nombre = 'f'
    líms = (0, 1)
    unids = None


class Triang(EcuaciónReprCoh):
    nombre = 'Triang'
    cls_ramas = [N, A, U, F]
    _cls_dist = estad.norm

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(c=cf['c'], loc=cf['u'], scale=cf['f'])
