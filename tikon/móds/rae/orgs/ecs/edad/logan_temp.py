import numpy as np
import scipy.stats as estad
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from .._plntll import EcuaciónOrg


class PrRhoLT(Parám):
    nombre = 'rho'
    líms = (0, 1)
    unids = 'días C -1'


class PrDeltaLT(Parám):
    nombre = 'delta'
    líms = (0, 1)
    unids = 'C'


class PrTLetalLT(Parám):
    nombre = 't_letal'
    líms = (None, None)
    unids = 'C'
    apriori = APrioriDist(estad.uniform(-10, 60))


class FuncLoganTemperatura(EcuaciónOrg):
    """
    Edad calculada con la taza de desarrollo de la ecuación de temperatura Logan:

    .. math::
        f(T) = \exp{\rho*T}-\exp{(\rho*T_l-(T_l-T)/\delta*T)}

    References
    ----------
    .. [1] Youngsoo Son y Lewis, Edwin E. 2005. Modelling temperature-dependent development and survival of
       Otiorhynchus sulcatus (Coleoptera: Curculionidae). Agricultural and Forest Entomology 7(3): 201–209.
    """
    nombre = 'Logan Temperatura'
    cls_ramas = [PrRhoLT, PrDeltaLT, PrTLetalLT]

    def eval(símismo, paso, sim):
        cf = símismo.cf

        temp_prom = símismo.obt_valor_extern(sim, 'clima.temp_prom')
        return np.maximum(
            np.exp(cf['rho'] * temp_prom) -
            np.exp(cf['rho'] * cf['t_letal'] - (cf['t_letal'] - temp_prom) / cf['delta']),
            0
        ) * paso

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_prom'}
