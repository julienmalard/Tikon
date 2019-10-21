from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.apli.ecs.utils import ECS_DECOMP
from tikon.móds.apli.utils import EJE_PRODUCTO, RES_DECOMP

from .exp_neg import DecaiExp


class EcuaciónDecomp(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [DecaiExp, EcuaciónVacía]
    _nombre_res = RES_DECOMP
    _eje_cosos = EJE_PRODUCTO


class EcsEdad(CategEc):
    nombre = ECS_DECOMP
    cls_ramas = [EcuaciónDecomp]
