from tikon.móds.rae.orgs.ecs.utils import ECS_CREC

from ..._plntll import EcuaciónOrg


class EcuaciónCrec(EcuaciónOrg):
    _nombre_res = ECS_CREC

    def eval(símismo, paso, sim):
        raise NotImplementedError
