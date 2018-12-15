from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónTransCoh


class K(Parám):
    nombre = 'k'
    líms = (0, None)


class Mu(Parám):
    nombre = 'mu'
    líms = (0, None)


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, None)


class T(EcuaciónTransCoh):
    nombre = 'T'
    cls_ramas = [K, Mu, Sigma]

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(loc=cf['mu'], scale=cf['sigma'], df=cf['k'])
