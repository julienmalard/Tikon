from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg
from tikon.móds.rae.utils import RES_TRANS


class EcuaciónTrans(EcuaciónOrg):
    _nombre_res = RES_TRANS

    def eval(símismo, paso, sim):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
