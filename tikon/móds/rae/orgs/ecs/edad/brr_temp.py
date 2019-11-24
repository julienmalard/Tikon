import numpy as np
from tikon.ecs.árb_mód import Parám

from .._plntll import EcuaciónOrg


class PrTDevMínBT(Parám):
    nombre = 't_dev_mín'
    líms = (None, None)
    unids = 'C'


class PrTLetalBT(Parám):
    nombre = 't_letal'
    líms = (None, None)
    unids = 'C'


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
    cls_ramas = [PrTDevMínBT, PrTLetalBT]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        temp_prom = símismo.obt_valor_extern(sim, 'clima.temp_prom')

        return (temp_prom * (temp_prom - cf['t_dev_mín']) * np.sqrt(cf['t_letal'] - temp_prom)) * paso

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_prom'}
