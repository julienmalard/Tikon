from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from .cauchy import Cauchy
from .constante import Constante
from .depred import Depred
from .gamma import Gamma
from .logística import Logística
from .normal import Normal
from .t import T
from .triang import Triang


class ProbRepr(SubcategEc):
    nombre = 'Prob'
    _cls_ramas = [EcuaciónVacía, Constante, Depred, Normal, Triang, Cauchy, Gamma, Logística, T]
    auto = Constante


class EcsRepr(CategEc):
    nombre = 'Reproducción'
    _cls_ramas = [ProbRepr]
