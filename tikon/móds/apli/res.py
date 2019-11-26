import numpy as np
from scipy.stats import expon
from tikon.central.res import Resultado
from tikon.ecs.aprioris import APrioriDist
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

    @property
    def unids(símismo):
        raise NotImplementedError


class ResDescomp(ResultadoApli):
    nombre = RES_DESCOMP
    unids = 'kg / ha / día'
    líms = (0, np.inf)


class ResConcentración(ResultadoApli):
    nombre = RES_CONC
    unids = 'kg / ha'
    líms = (0, np.inf)
    apriori = APrioriDist(expon(scale=5))
    inicializable = True


class ResMortalidad(ResultadoApli):
    líms = (0, 1)
    nombre = RES_MRTLD
    unids = 'individuos'

    def __init__(símismo, sim, coords, vars_interés):
        coords = {
            EJE_ETAPA: sim.simul_exper.modelo[RedAE.nombre].etapas, **coords
        }
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)
