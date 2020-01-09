import numpy as np
from scipy.stats import expon
from tikon.central.res import Resultado
from tikon.ecs.aprioris import APrioriDist
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.utils import EJE_ETAPA

from .utils import RES_DESCOMP, RES_DENS, RES_CAPTURA, EJE_TRAMPA


class ResultadoTrampa(Resultado):
    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_TRAMPA: sim.mód.trampas, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

    @property
    def nombre(símismo):
        raise NotImplementedError

    @property
    def unids(símismo):
        raise NotImplementedError


class ResDescomp(ResultadoTrampa):
    nombre = RES_DESCOMP
    unids = 'trampas / ha / día'
    líms = (0, np.inf)


class ResDensidad(ResultadoTrampa):
    nombre = RES_DENS
    unids = 'trampas / ha'
    líms = (0, np.inf)
    apriori = APrioriDist(expon(scale=5))
    inicializable = True


class ResCaptura(ResultadoTrampa):
    líms = (0, None)
    nombre = RES_CAPTURA
    unids = None

    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_ETAPA: sim.simul_exper.modelo[RedAE.nombre].etapas, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)
