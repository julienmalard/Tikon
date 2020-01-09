from tikon.móds.rae.utils import EJE_ETAPA

from .._plntll import EcuaciónTrampa
from ...utils import RES_CAPTURA


class EcuaciónCaptura(EcuaciónTrampa):
    _nombre_res = RES_CAPTURA
    eje_cosos = EJE_ETAPA

    @property
    def nombre(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        raise NotImplementedError
