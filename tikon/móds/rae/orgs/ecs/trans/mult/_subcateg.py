from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.red.utils import RES_TRANS

from .linear import Linear


class MultTrans(SubcategEcOrg):
    """
    Posibilidades de transiciones multiplicadoras (por ejemplo, la eclosión de parasitoides).
    """

    nombre = 'Mult'
    cls_ramas = [EcuaciónVacía, Linear]
    _nombre_res = RES_TRANS
