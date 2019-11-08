from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.red.utils import RES_CREC

from .lognorm_temp import LogNormTemp
from .ninguna import Ninguna


class ModifCrec(SubcategEcOrg):
    nombre = 'Modif'
    cls_ramas = [EcuaciónVacía, Ninguna, LogNormTemp]
    _nombre_res = RES_CREC
