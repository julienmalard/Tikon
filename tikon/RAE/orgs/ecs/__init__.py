from .edad import ecs_edad
from .estoc import ecs_estoc
from .mov import ecs_mov
from .muert import ecs_muert
from .repr import ecs_repr
from .trans import ecs_trans
from .depred import ecs_depred
from .crec import ecs_crec
from tikon.ecs import ÁrbolEcs


ecs_etps_orgs = ÁrbolEcs(
    'organismo',
    categs=[ecs_crec, ecs_depred, ecs_muert, ecs_edad, ecs_trans, ecs_repr, ecs_mov, ecs_estoc]
)
