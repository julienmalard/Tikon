import numpy as np
import scipy.stats as estad

from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.utils import RES_TRANS
from .._plntll_ec import EcuaciónTrans


class A(Parám):
    nombre = 'a'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(estad.expon(scale=100))


class Linear(EcuaciónTrans):
    nombre = 'Linear'
    cls_ramas = [A]
    _nombre_res = RES_TRANS

    def eval(símismo, paso, sim):
        trans = símismo.obt_valor_res(sim)
        return (símismo.cf['a'] * trans).fi(np.round)
