import numpy as np
from scipy.stats import norm, expon
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónMuertes


class M(Parám):
    nombre = 'm'
    líms = (0, None)
    unids = 'mm -1'
    apriori = APrioriDist(expon(scale=10))


class B(Parám):
    nombre = 'b'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(expon(scale=10))


class LluviaLinear(EcuaciónMuertes):
    """
    ராமோனியாவின் யோசனை
    """

    nombre = 'Lluvia linear'
    cls_ramas = [M, B]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        lluvia = símismo.obt_valor_extern(sim, 'clima.precip')
        return min(cf['m'] * lluvia + cf['b'], 1)

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.precip'}
