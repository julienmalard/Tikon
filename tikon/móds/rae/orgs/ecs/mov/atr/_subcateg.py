from tikon.ecs import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.utils import RES_MOV

from .dif import DifusiónAleatoria


class Atracción(SubcategEcOrg):
    nombre = 'Atracción'
    cls_ramas = [
        DifusiónAleatoria, EcuaciónVacía
    ]
    _nombre_res = RES_MOV
