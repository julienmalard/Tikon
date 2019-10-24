from ..._ecs_coh import EcuaciónConCohorte
from ..._plntll_ec import EcuaciónOrg


class EcuaciónTransCoh(EcuaciónConCohorte):
    _nombre_res = TRANS

    def _prms_scipy(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        return símismo.trans_cohortes(símismo.cambio_edad(), símismo.dist, quitar=True)


class EcuaciónTrans(EcuaciónOrg):
    _nombre_res = TRANS

    def eval(símismo, paso, sim):
        raise NotImplementedError
