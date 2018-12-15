from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónRepr
import scipy.stats as estad

class N(Parám):
    nombre = 'n'
    líms = (0, None)


class Mu(Parám):
    nombre = 'mu'
    líms = (0, None)


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, None)


class Normal(EcuaciónRepr):
    """

    """
    nombre = 'Normal'
    cls_ramas = [N, Mu, Sigma]
    _cls_dist = estad.norm

    def _prms_scipy(símismo):
        return dict(loc=símismo._ramas['mu'], scale=símismo._ramas['sigma'])
