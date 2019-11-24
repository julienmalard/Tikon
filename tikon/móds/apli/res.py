import numpy as np
from tikon.central.res import Resultado
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.utils import EJE_ETAPA

from .utils import RES_DESCOMP, RES_CONC, RES_MRTLD, EJE_PRODUCTO


class ResultadoApli(Resultado):
    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_PRODUCTO: sim.productos, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

    @property
    def nombre(símismo):
        raise NotImplementedError


class ResDescomp(Resultado):
    líms = (0, np.nan)
    nombre = RES_DESCOMP
    unids = 'kg / ha / día'


class ResConcentración(Resultado):
    nombre = RES_CONC
    unids = 'kg / ha'
    líms = (0, np.nan)
    inicializable = True


class ResMortalidad(Resultado):
    líms = (0, 1)
    nombre = RES_MRTLD
    unids = 'individuos'

    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_ETAPA: sim.simul_exper[RedAE.nombre].etapas, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)
