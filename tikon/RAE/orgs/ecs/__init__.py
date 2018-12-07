from .edad import EcsEdad
from .estoc import EcsEstoc
from .mov import EcsMov
from .muertes import EcsMuerte
from .repr import EcsRepr
from .trans import EcsTrans
from .depred import EcsDepred
from .crec import EcsCrec
from tikon.ecs import ÁrbolEcs


class EcsOrgs(ÁrbolEcs):
    nombre = 'organismo'
    _cls_ramas = [EcsCrec, EcsDepred, EcsMuerte, EcsEdad, EcsTrans, EcsRepr, EcsMov, EcsEstoc]

