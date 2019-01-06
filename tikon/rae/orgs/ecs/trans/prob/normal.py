import scipy.stats as estad

from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónTransCoh


class Mu(Parám):
    nombre = 'mu'
    líms = (0, None)


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, None)


class Normal(EcuaciónTransCoh):

    def _prms_scipy(símismo):
        return dict(loc=símismo.cf['mu'], scale=símismo.cf['sigma'])

    nombre = 'Normal'
    cls_ramas = [Mu, Sigma]
    _cls_dist = estad.norm
