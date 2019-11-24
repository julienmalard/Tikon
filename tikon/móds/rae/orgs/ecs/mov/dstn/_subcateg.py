from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.orgs.ecs.mov.dstn.eucld import Euclidiana
from tikon.móds.rae.utils import RES_MOV


class Distancia(SubcategEcOrg):
    nombre = 'Distancia'
    cls_ramas = [
        Euclidiana, EcuaciónVacía
    ]
    _nombre_res = RES_MOV
