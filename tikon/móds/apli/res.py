import numpy as np
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.red.utils import EJE_ETAPA
from tikon.result.res import Resultado

from .utils import RES_DECOMP, RES_CONC, RES_MRTLD, EJE_PRODUCTO


class ResultadoApli(Resultado):
    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_PRODUCTO: sim.productos, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

    @property
    def nombre(símismo):
        raise NotImplementedError


class ResDecomp(Resultado):
    líms = (0, np.nan)
    nombre = RES_DECOMP
    unids = 'kg / ha / día'


class ResConcentración(Resultado):
    líms = (0, np.nan)
    nombre = RES_CONC
    unids = 'kg / ha'


class ResMortalidad(Resultado):
    líms = (0, 1)
    nombre = RES_MRTLD
    unids = 'individuos'

    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_ETAPA: sim.simul_exper[RedAE.nombre].etapas, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)
