from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.utils import RES_TRANS

from .cauchy import Cauchy
from .constante import Constante
from .gamma import Gamma
from .logística import Logística
from .normal import Normal
from .t import T
from .triang import Triang


class ProbTrans(SubcategEcOrg):
    nombre = 'Prob'
    cls_ramas = [Normal, EcuaciónVacía, Cauchy, Constante, Gamma, Logística, T, Triang]
    _nombre_res = RES_TRANS
