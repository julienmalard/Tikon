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

    def verificar(símismo, org):
        # Si crec Ec está activada, solamente Depred y Estoc se pueden activar
        # No repr en etapas otras que adulto
        # Etapa sin crec y con Trans que falta
        # Etapa con cohortes sin edad -> activar edad días
        # Etapa con mult pero no prob o deter para trans
        # Etapa con trans prob y deter activados
        # Org con múltiples etapas sin trans
        # Mov atr pero no mov dstn -> activar dstn Euclidiana
        # Crec tasa pero no ec
        # Crec ec pero no tasa -> activar tasa Ninguna
        pass  # para hacer
