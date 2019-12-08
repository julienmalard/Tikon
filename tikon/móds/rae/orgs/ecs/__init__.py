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
        # Si crec Ec está activada, solamente Depred y Estoc se pueden activar
        # No repr en etapas otras que adulto
        # Etapa sin crec y con Trans que falta
        # Etapa con cohortes sin edad
        pass  # para hacer
