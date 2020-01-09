from tikon.móds.rae.utils import RES_EDAD

from .._plntll import EcuaciónOrg


class EcuaciónEdad(EcuaciónOrg):
    _nombre_res = RES_EDAD

    def eval(símismo, paso, sim):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
