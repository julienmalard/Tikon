import numpy as np
from tikon.móds.rae.red.utils import EJE_ETAPA
from tikon.result.res import Resultado

RES_BIOMASA = 'biomasa'
RES_HUMSUELO = 'humedad suelo'


class ResBiomasa(Resultado):
    líms = (0, np.nan)
    nombre = RES_BIOMASA
    unids = '[kg o m2] / ha'

    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_ETAPA: sim.etapas, **coords}
        super().__init__(sim, coords, vars_interés)


class ResHumedadSuelo(Resultado):
    líms = (0, np.nan)
    nombre = RES_HUMSUELO
    unids = 'cm3 / cm3'
