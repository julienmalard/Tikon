from tikon.móds.rae.utils import RES_MRTE

from .._plntll import EcuaciónOrg


class EcuaciónMuertes(EcuaciónOrg):
    _nombre_res = RES_MRTE

    def eval(símismo, paso, sim):
        """Debe devolver la taza de mortalidad por paso (es decir, ignorando el valor de `paso`."""
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
