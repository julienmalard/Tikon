import numpy as np
from scipy.stats import norm, expon
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from .._plntll import EcuaciónOrg


class PrTDevMínBT(Parám):
    nombre = 't_dev_mín'
    líms = (None, None)
    unids = 'C'
    apriori = APrioriDist(norm(20, 10))


class PrDeltaTLetalBT(Parám):
    nombre = 'delta_t_letal'
    líms = (0, None)
    unids = 'C'
    apriori = APrioriDist(expon(scale=10))


class FuncBrièreTemperatura(EcuaciónOrg):
    """
    Edad calculada con la taza de desarrollo de la ecuación de temperatura Brère.

    .. math::
        f(T) = T(T-T_b)\sqrt{(T_l-T)}

    En esta ecuación, tal como en las otras con taza de desarrollo, quitamos el parámetro típicamente multiplicado por
    toda la ecuación, porque eso duplicaría el propósito del parámetro de ubicación de las distribuciones
    de probabilidad empleadas después.

    References
    ----------
    .. [1] Mokhtar, Abrul Monim y Salem Saif al Nabhani. 2010. Temperature-dependent development of dubas bug,
        Ommatissus lybicus (Hemiptera: Tropiduchidae), an endemic pest of date palm, Phoenix dactylifera.
        Eur. J. Entomol. 107: 681–685.
    """
    nombre = 'Brière Temperatura'
    cls_ramas = [PrTDevMínBT, PrDeltaTLetalBT]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        temp_prom = símismo.obt_valor_extern(sim, 'clima.temp_prom')

        return np.maximum(
            temp_prom * (temp_prom - cf['t_dev_mín']), 0
        ) * np.sqrt(
            np.maximum(cf['delta_t_letal'] + cf['t_dev_mín'] - temp_prom, 0)
        ) * paso

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_prom'}
