from tikon.ecs import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.utils import RES_MOV

from .decai_exp import DecaiExpon
from .dif import DifusiónAleatoria


class Atracción(SubcategEcOrg):
    nombre = 'Atracción'
    cls_ramas = [
        EcuaciónVacía, DifusiónAleatoria, DecaiExpon
    ]
    _nombre_res = RES_MOV
