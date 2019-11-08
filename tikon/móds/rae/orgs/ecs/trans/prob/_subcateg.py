from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.red.utils import RES_TRANS

from .cauchy import Cauchy
from .constante import Constante
from .gamma import Gamma
from .logística import Logística
from .normal import Normal


class ProbTrans(SubcategEcOrg):
    nombre = 'Prob'
    cls_ramas = [Normal, EcuaciónVacía, Cauchy, Constante, Gamma, Logística]
    _nombre_res = RES_TRANS
