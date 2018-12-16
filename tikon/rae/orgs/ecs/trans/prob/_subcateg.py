from tikon.ecs.árb_mód import SubcategEc, EcuaciónVacía
from .cauchy import Cauchy
from .constante import Constante
from .gamma import Gamma
from .logística import Logística
from .normal import Normal


class ProbTrans(SubcategEc):
    nombre = 'Prob'
    cls_ramas = [EcuaciónVacía, Cauchy, Constante, Gamma, Logística, Normal]
    auto = Normal
    _nombre_res = 'Transiciones'
    _eje_cosos = 'etapa'
