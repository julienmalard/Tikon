from tikon.ecs.árb_mód import Ecuación, SubcategEc, CategEc
from tikon.móds.rae.utils import EJE_ETAPA, RES_POBS, RES_COHORTES


class CategEcOrg(CategEc):
    eje_cosos = EJE_ETAPA

    def pobs(símismo, sim, filtrar=True):
        return símismo.obt_valor_mód(sim, RES_POBS, filtrar=filtrar)

    def ajust_pobs(símismo, sim, pobs):
        símismo.poner_valor_mód(sim, var=RES_POBS, val=pobs, rel=True)

    @property
    def nombre(símismo):
        raise NotImplementedError


class SubcategEcOrg(SubcategEc):
    eje_cosos = EJE_ETAPA

    def pobs(símismo, sim, filtrar=True):
        return símismo.obt_valor_mód(sim, RES_POBS, filtrar=filtrar)

    def ajust_pobs(símismo, sim, pobs):
        símismo.poner_valor_mód(sim, var=RES_POBS, val=pobs, rel=True)

    @classmethod
    def registrar_ec(cls, ec):
        cls.cls_ramas.append(ec)

    @property
    def nombre(símismo):
        raise NotImplementedError


class EcuaciónOrg(Ecuación):
    eje_cosos = EJE_ETAPA

    def pobs(símismo, sim, filtrar=True):
        return símismo.obt_valor_mód(sim, RES_POBS, filtrar=filtrar)

    def eval(símismo, paso, sim):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError

    @property
    def _nombre_res(símismo):
        raise NotImplementedError
