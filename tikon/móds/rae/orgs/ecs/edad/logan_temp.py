import numpy as np
import scipy.stats as estad
from tikon.central.matriz import máximo
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónEdad


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
    apriori = APrioriDist(estad.norm(20, 10))


class FuncLoganTemperatura(EcuaciónEdad):
    """
    Edad calculada con la taza de desarrollo de la ecuación de temperatura Logan:

    .. math::
        f(T) = \exp{\rho*T}-\exp{(\rho*T_l-(T_l-T)/\delta*T)}

    References
    ----------
    .. [1] Youngsoo Son y Lewis, Edwin E. 2005. Modelling temperature-dependent development and survival of
       Otiorhynchus sulcatus (Coleoptera: Curculionidae). Agricultural and Forest Entomology 7(3): 201–209.
    .. [2] Logan, J.A., Wollkind, D.J., Hoyt, S.C. & Tanigoshi, L.K. 1976. An analytical model for description of
       temperature dependent rate phenomena in arthropods. Environmental Entomology, 5:1133–1140.
    """
    nombre = 'Logan Temperatura'
    cls_ramas = [PrRhoLT, PrDeltaLT, PrTLetalLT]

    def eval(símismo, paso, sim):
        cf = símismo.cf

        temp_prom = símismo.obt_valor_extern(sim, 'clima.temp_prom')
        return máximo(
            (cf['rho'] * temp_prom).fi(np.exp) -
            (cf['rho'] * cf['t_letal'] - (cf['t_letal'] - temp_prom) / cf['delta']).fi(np.exp),
            0
        ) * paso

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_prom'}
