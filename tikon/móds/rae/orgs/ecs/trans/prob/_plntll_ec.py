from .._plntll_ec import EcuaciónTrans

from ..._ecs_coh import EcuaciónConCohorte


class EcuaciónTransCoh(EcuaciónTrans, EcuaciónConCohorte):

    def eval(símismo, paso, sim):
        return símismo.trans_cohortes(sim, símismo.cambio_edad(sim), dist=símismo.dist)

    @property
    def _cls_dist(símismo):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError

    def _prms_scipy(símismo):
        raise NotImplementedError
