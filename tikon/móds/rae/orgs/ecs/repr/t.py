import scipy.stats as estad
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs.repr._plntll_ec import EcuaciónReprCoh


class N(Parám):
    nombre = 'n'
    líms = (0, None)
    unids = None


class K(Parám):
    nombre = 'k'
    líms = (0, None)
    unids = None


class Mu(Parám):
    nombre = 'mu'
    líms = (0, None)
    unids = None


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, None)
    unids = None


class T(EcuaciónReprCoh):
    nombre = 'T'
    cls_ramas = [N, K, Mu, Sigma]
    _cls_dist = estad.t

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(df=cf['k'], loc=cf['mu'], scale=cf['sigma'])
