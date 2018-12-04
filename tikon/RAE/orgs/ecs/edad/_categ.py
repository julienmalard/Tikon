from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from .brr_no_lín_temp import FuncBrièreNoLinearTemperatura
from .brr_temp import FuncBrièreTemperatura
from .d_grados import FuncDíasGrados
from .días import FuncDías
from .logan_temp import FuncLoganTemperatura


class EcuaciónEdad(SubcategEc):
    nombre = 'Ecuación'
    _cls_ramas = [
        EcuaciónVacía,
        FuncDías, FuncDíasGrados, FuncBrièreTemperatura, FuncLoganTemperatura, FuncBrièreNoLinearTemperatura
    ]
    auto = FuncDías


class EcsEdad(CategEc):
    nombre = 'Edad'
    _cls_ramas = [EcuaciónEdad]
