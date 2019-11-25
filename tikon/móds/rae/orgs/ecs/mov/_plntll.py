from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg
from tikon.móds.rae.utils import RES_MOV
from tikon.utils import EJE_DEST


class PlantillaEcDifusión(EcuaciónOrg):
    _nombre_res = RES_MOV

    def eval(símismo, paso, sim):
        d = símismo.cf['d']
        pobs = símismo.pobs(sim)

        atr = símismo.calc_atr(paso, sim)

        dsnt = símismo.obt_valor_res(sim)
        atr_ajust = (atr * d / dsnt).fillna(1)  # Atracción ajustada por distancia. 1 = no atracción neta

        probs = atr_ajust / atr_ajust.sum(dim=EJE_DEST)  # Normalizar probabilidades para sumar a 1

        return probs * pobs

    def calc_atr(símismo, paso, sim):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
