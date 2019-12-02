import numpy as np
from scipy.stats import norm, expon
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from .._plntll import EcuaciónOrg


class PrTDevMínBNLT(Parám):
    nombre = 't_dev_mín'
    líms = (None, None)
    unids = 'C'
    apriori = APrioriDist(norm(20, 10))


class PrDeltaTLetalBNLT(Parám):
    nombre = 'delta_t_letal'
    líms = (0, None)
    unids = 'C'
    apriori = APrioriDist(expon(scale=10))


class PrMBNLT(Parám):
    nombre = 'm'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(expon(scale=10))


class FuncBrièreNoLinearTemperatura(EcuaciónOrg):
    """
    Edad calculada con la taza de desarrollo de la ecuación de temperatura no linear de Brière.

    .. math::
        f(T) = T(T-T_b)(T_l-T)^(1/m)

    En esta ecuación, tal como en las otras con taza de desarrollo, quitamos el parámetro típicamente multiplicado por
    toda la ecuación, porque eso duplicaría el propósito del parámetro de ubicación de las distribuciones
    de probabilidad empleadas después.

    References
    ----------
    .. [1] Youngsoo Son et al. 2012. Estimation of developmental parameters for adult emergence of Gonatocerus
       morgani, a novel egg parasitoid of the glassy-winged sharpshooter, and development of a degree-day
       model. Biological Control 60(3): 233-260.
    .. [2] J.-F. Briere, P. Pracros, A.-Y. Le Broux, J.-S. Pierre. A novel rate model of temperature-dependent
       development for arthropods Environmental Entomology, 28 (1999), pp. 22-29.
    """

    nombre = 'Brière No Linear Temperatura'
    cls_ramas = [PrTDevMínBNLT, PrDeltaTLetalBNLT, PrMBNLT]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        temp_prom = símismo.obt_valor_extern(sim, 'clima.temp_prom')
        return np.maximum(
            temp_prom * (temp_prom - cf['t_dev_mín']), 0
        ) * np.power(
            np.maximum(cf['t_dev_mín'] + cf['delta_t_letal'] - temp_prom, 0),
            1 / cf['m']
        ) * paso

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_prom'}
