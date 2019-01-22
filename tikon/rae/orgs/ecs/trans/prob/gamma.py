from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónTransCoh


class U(Parám):
    nombre = 'u'
    líms = (0, None)


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class F(Parám):
    nombre = 'f'
    líms = (0, None)


class Gamma(EcuaciónTransCoh):
    nombre = 'Gamma'
    cls_ramas = [U, F, A]

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(loc=cf['u'], scale=cf['f'], a=cf['a'])
