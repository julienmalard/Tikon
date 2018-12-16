import numpy as np

from tikon.ecs.árb_mód import Parám
from .._plntll_ec import EcuaciónOrg


class PrRhoLT(Parám):
    nombre = 'rho'
    líms = (0, 1)


class PrDeltaLT(Parám):
    nombre = 'delta'
    líms = (0, 1)


class PrTLetalLT(Parám):
    nombre = 't_letal'
    líms = (None, None)


class FuncLoganTemperatura(EcuaciónOrg):
    """
    Edad calculada con la taza de desarrollo de la ecuación de temperatura Logan:

    Youngsoo Son y Lewis, Edwin E. 2005. Modelling temperature-dependent development and survival of
      Otiorhynchus sulcatus (Coleoptera: Curculionidae). Agricultural and Forest Entomology 7(3): 201–209.
    """
    nombre = 'Logan Temperatura'
    cls_ramas = [PrDeltaLT, PrTLetalLT]

    def eval(símismo, paso):
        mnjdr_móds = símismo.mnjdr_móds
        cf = símismo.cf

        return (np.exp(cf['rho'] * mnjdr_móds['clima.temp_prom']) -
                np.exp(cf['rho'] * cf['t_letal'] - (cf['t_letal'] - mnjdr_móds['clima.temp_prom']) / cf['delta'])
                ) * paso
