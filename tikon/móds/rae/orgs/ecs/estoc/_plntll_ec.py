from tikon.móds.rae.utils import RES_ESTOC

from .._plntll import EcuaciónOrg


class EcuaciónEstoc(EcuaciónOrg):
    _nombre_res = RES_ESTOC

    def eval(símismo, paso, sim):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
