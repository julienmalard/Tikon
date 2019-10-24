from tikon.ecs import ÁrbolEcs
from .crec import EcsCrec
from .depred import EcsDepred
from .edad import EcsEdad
from .estoc import EcsEstoc
from .mov import EcsMov
from .muertes import EcsMuerte
from .repr import EcsRepr
from .trans import EcsTrans


class EcsOrgs(ÁrbolEcs):
    nombre = 'organismo'

    # ¡Este órden queda muy importante!
    cls_ramas = [EcsEdad, EcsDepred, EcsCrec, EcsRepr, EcsMuerte, EcsTrans, EcsMov, EcsEstoc]

    def verificar(símismo):
        pass  # para hacer
