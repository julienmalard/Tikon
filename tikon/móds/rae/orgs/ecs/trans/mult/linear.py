from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.utils import RES_TRANS

from ..._plntll import EcuaciónOrg


class A(Parám):
    nombre = 'a'
    líms = (0, None)
    unids = None


class Linear(EcuaciónOrg):
    nombre = 'Linear'
    cls_ramas = [A]
    _nombre_res = RES_TRANS

    def eval(símismo, paso, sim):
        trans = símismo.obt_valor_res(sim)
        return (símismo.cf['a'] * trans).round()
