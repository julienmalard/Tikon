from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónTransCoh


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class B(Parám):
    nombre = 'b'
    líms = (0, None)


class C(Parám):
    nombre = 'c'
    líms = (0, None)


class Triang(EcuaciónTransCoh):
    nombre = 'Triang'
    cls_ramas = [A, B, C]

    def _prms_scipy(símismo):
        cf = símismo.cf
        return dict(loc=cf['a'], scale=cf['b'], c=cf['c'])
