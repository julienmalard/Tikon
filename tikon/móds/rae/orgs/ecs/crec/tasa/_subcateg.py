from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.utils import RES_CREC

from .lognorm_temp import LogNormTemp
from .constante import Constante


class TasaCrec(SubcategEcOrg):
    nombre = 'Tasa'
    cls_ramas = [EcuaciónVacía, Constante, LogNormTemp]
    _nombre_res = RES_CREC
