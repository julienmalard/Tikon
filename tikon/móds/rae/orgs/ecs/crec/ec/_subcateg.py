from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.red.utils import RES_CREC

from .const import Constante
from .expon import Expon
from .logíst import Logíst
from .logíst_depred import LogístDepred
from .logíst_presa import LogístPresa


class EcuaciónCrec(SubcategEcOrg):
    nombre = 'Ecuación'
    cls_ramas = [EcuaciónVacía, Expon, Logíst, LogístPresa, LogístDepred, Constante]
    _nombre_res = RES_CREC
