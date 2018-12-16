from tikon.ecs.árb_mód import Ecuación, Parám
from ._plntll_ec import EcuaciónTransCoh


class U(Parám):
    nombre = 'u'
    líms = (0, None)


class F(Parám):
    nombre = 'f'
    líms = (0, None)


class Cauchy(EcuaciónTransCoh):
    nombre = 'Cauchy'
    cls_ramas = [U, F]

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(loc=cf['u'], scale=cf['f'])
