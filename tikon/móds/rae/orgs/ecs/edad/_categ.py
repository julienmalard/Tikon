from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import CategEcOrg, SubcategEcOrg
from tikon.móds.rae.orgs.ecs.utils import ECS_EDAD
from tikon.móds.rae.utils import RES_EDAD

from .brr_no_lín_temp import FuncBrièreNoLinearTemperatura
from .brr_temp import FuncBrièreTemperatura
from .d_grados import FuncDíasGradosSH, FuncDíasGradosSI, FuncDíasGradosSN, FuncDíasGradosSV, \
    FuncDíasGradosTH, FuncDíasGradosTI, FuncDíasGradosTN, FuncDíasGradosTV
from .días import FuncDías
from .logan_temp import FuncLoganTemperatura


class EcEdad(SubcategEcOrg):
    nombre = 'Ecuación'
    cls_ramas = [
        FuncDías,
        FuncDíasGradosSH, FuncDíasGradosSI, FuncDíasGradosSN, FuncDíasGradosSV,
        FuncDíasGradosTH, FuncDíasGradosTI, FuncDíasGradosTN, FuncDíasGradosTV,
        FuncBrièreTemperatura, FuncLoganTemperatura, FuncBrièreNoLinearTemperatura,
        EcuaciónVacía
    ]
    _nombre_res = RES_EDAD


class EcsEdad(CategEcOrg):
    nombre = ECS_EDAD
    cls_ramas = [EcEdad]
