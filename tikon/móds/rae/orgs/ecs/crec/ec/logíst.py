from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónCrec


class K(Parám):
    nombre = 'K'
    líms = (0, None)
    unids = 'individual'


class Logíst(EcuaciónCrec):
    """
    Crecimiento logístico.
    """

    nombre = 'Logístico'
    cls_ramas = [K]

    def eval(símismo, paso, sim):
        pobs_etps = símismo.pobs(sim)
        return símismo.obt_valor_res(sim) * pobs_etps * (1 - pobs_etps / símismo.cf['K'])
