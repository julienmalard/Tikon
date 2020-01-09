from tikon.móds.rae.utils import EJE_ETAPA

from .._plntll import EcuaciónProd
from ...utils import RES_MRTLD


class EcuaciónMortalidad(EcuaciónProd):
    _nombre_res = RES_MRTLD
    eje_cosos = EJE_ETAPA

    @property
    def nombre(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        raise NotImplementedError
