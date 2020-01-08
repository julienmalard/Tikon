from tikon.móds.rae.utils import RES_CREC

from ..._plntll import EcuaciónOrg


class ModCrec(EcuaciónOrg):
    _nombre_res = RES_CREC

    @property
    def nombre(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        raise NotImplementedError
