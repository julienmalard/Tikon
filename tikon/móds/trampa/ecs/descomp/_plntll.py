from tikon.móds.trampa.utils import RES_DESCOMP

from .._plntll import EcuaciónTrampa


class EcuaciónDescomp(EcuaciónTrampa):
    _nombre_res = RES_DESCOMP

    @property
    def nombre(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        raise NotImplementedError
