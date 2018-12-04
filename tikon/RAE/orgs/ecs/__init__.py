from .edad import ecs_edad
from .estoc import EcsEstoc
from .mov import ecs_mov
from tikon.RAE.orgs.ecs.muertes._categ import ecs_muert
from .repr import ecs_repr
from tikon.RAE.orgs.ecs.trans._categ import ecs_trans
from .depred import EcsDepred
from .crec import ecs_crec
from tikon.ecs import ÁrbolEcs


ecs_etps_orgs = ÁrbolEcs(
    'organismo',
    categs=[ecs_crec, ecs_depred, ecs_muert, ecs_edad, ecs_trans, ecs_repr, ecs_mov, ecs_estoc]
)
