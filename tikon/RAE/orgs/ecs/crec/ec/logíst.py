from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónCrec


class K(Parám):
    nombre = 'K'
    líms = (0, None)


class Logíst(EcuaciónCrec):
    """
    Crecimiento logístico.
    """

    nombre = 'Logístico'
    _cls_ramas = [K]

    def __call__(símismo, paso):
        pobs_etps = símismo.pobs_etps()
        return símismo.crec_etps() * pobs_etps * (1 - pobs_etps / símismo.cf['K'])
