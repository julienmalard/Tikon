from tikon.ecs.árb_mód import EcuaciónVacía
from .const import Constante
from .expon import Expon
from .logíst import Logíst
from .logíst_depred import LogístDepred
from .logíst_presa import LogístPresa
from ....ecs._plntll import SubcategEcOrg
from tikon.móds.rae.utils import RES_CREC


class EcuaciónCrec(SubcategEcOrg):
    nombre = 'Ecuación'
    cls_ramas = [EcuaciónVacía, Expon, Logíst, LogístPresa, LogístDepred, Constante]
    _nombre_res = RES_CREC
