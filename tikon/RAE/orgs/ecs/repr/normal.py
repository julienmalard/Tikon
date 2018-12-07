from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónRepr


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
    _cls_ramas = [N, Mu, Sigma]

    def _prms_scipy(símismo):
        return dict(loc=símismo._ramas['mu'], scale=símismo._ramas['sigma'])
