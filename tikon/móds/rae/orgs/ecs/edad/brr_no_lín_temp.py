import numpy as np
from tikon.ecs.árb_mód import Parám

from .._plntll import EcuaciónOrg


class PrTDevMínBNLT(Parám):
    nombre = 't_dev_mín'
    líms = (None, None)
    unids = 'C'


class PrTLetalBNLT(Parám):
    nombre = 't_letal'
    líms = (None, None)
    unids = 'C'


class PrMBNLT(Parám):
    nombre = 'm'
    líms = (0, None)
    unids = None


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
    cls_ramas = [PrTDevMínBNLT, PrTLetalBNLT, PrMBNLT]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        temp_prom = símismo.obt_valor_extern(sim, 'clima.temp_prom')
        return (temp_prom * (temp_prom - cf['t_dev_mín']) * np.power(cf['t_letal'] - temp_prom, 1 / cf['m'])) * paso

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_prom'}
