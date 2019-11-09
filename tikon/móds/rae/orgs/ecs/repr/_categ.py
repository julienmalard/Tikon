from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg, CategEcOrg
from tikon.móds.rae.orgs.ecs.utils import ECS_REPR
from tikon.móds.rae.red.utils import RES_REPR, EJE_ETAPA

from .cauchy import Cauchy
from .constante import Constante
from .depred import Depred
from .gamma import Gamma
from .logística import Logística
from .normal import Normal
from .t import T
from .triang import Triang


class ProbRepr(SubcategEcOrg):
    nombre = 'Prob'
    cls_ramas = [Constante, EcuaciónVacía, Depred, Normal, Triang, Cauchy, Gamma, Logística, T]
    _nombre_res = RES_REPR


class EcsRepr(CategEcOrg):
    nombre = ECS_REPR
    cls_ramas = [ProbRepr]

    def postproc(símismo, paso, sim):
        # Agregar las reproducciones a las poblaciones
        reprod = símismo.obt_valor_res(sim).round()
        reprod[EJE_ETAPA] = sim.etps_repr
        símismo.poner_valor_res(sim, reprod)

        símismo.ajust_pobs(sim, reprod)
