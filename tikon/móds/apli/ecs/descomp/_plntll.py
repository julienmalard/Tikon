from tikon.móds.apli.utils import RES_DESCOMP

from .._plntll import EcuaciónProd


class EcuaciónDescomp(EcuaciónProd):
    _nombre_res = RES_DESCOMP

    @property
    def nombre(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        raise NotImplementedError
