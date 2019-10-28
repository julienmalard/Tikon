from tikon.ecs.árb_mód import Ecuación, SubcategEc, CategEc
from tikon.móds.rae.red.utils import EJE_ETAPA, RES_POBS


class CategEcOrg(CategEc):
    _eje_cosos = EJE_ETAPA

    def pobs(símismo, sim, filtrar=True):
        return símismo.obt_val_mód(sim, RES_POBS, filtrar=filtrar)

    def ajust_pobs(símismo, sim, pobs):
        símismo.poner_val_mód(sim, var=RES_POBS, val=pobs)

    @property
    def nombre(símismo):
        raise NotImplementedError


class SubcategEcOrg(SubcategEc):
    _eje_cosos = EJE_ETAPA

    def pobs(símismo, sim, filtrar=True):
        return símismo.obt_val_mód(sim, RES_POBS, filtrar=filtrar)

    @property
    def nombre(símismo):
        raise NotImplementedError


class EcuaciónOrg(Ecuación):
    _eje_cosos = EJE_ETAPA

    def pobs(símismo, sim, filtrar=True):
        return símismo.obt_val_mód(sim, RES_POBS, filtrar=filtrar)

    def eval(símismo, paso, sim):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
