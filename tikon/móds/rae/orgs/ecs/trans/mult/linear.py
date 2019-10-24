import numpy as np

from tikon.ecs.árb_mód import Parám
from ..._plntll_ec import EcuaciónOrg


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class Linear(EcuaciónOrg):
    nombre = 'Linear'
    cls_ramas = [A]
    _nombre_res = TRANS

    def eval(símismo, paso, sim):
        trans = símismo.obt_res(filtrar=True)
        trans *= símismo.cf['a']
        return np.round(trans)
