import numpy as np
from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg
from tikon.móds.rae.utils import RES_MOV
from tikon.utils import EJE_DEST


class EcuaciónMov(EcuaciónOrg):
    _nombre_res = RES_MOV

    def eval(símismo, paso, sim):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError


class PlantillaEcDifusión(EcuaciónMov):

    def eval(símismo, paso, sim):
        pobs = símismo.pobs(sim)

        atr = símismo.calc_atr(sim)

        dsnt = símismo.obt_valor_res(sim)
        atr_ajust = (atr / dsnt)  # Atracción ajustada por distancia. 1 = no atracción neta
        atr_ajust = atr_ajust.donde(atr_ajust.f(np.isfinite), 1)
        probs = atr_ajust / atr_ajust.suma(dim=EJE_DEST)  # Normalizar probabilidades para sumar a 1

        return probs * pobs

    def calc_atr(símismo, sim):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
