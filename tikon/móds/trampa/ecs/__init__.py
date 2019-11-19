from tikon.ecs import ÁrbolEcs

from .decai import EcsDecai
from .mrtld import EcsMortalidad


class EcsTrampa(ÁrbolEcs):
    nombre = 'trampa'

    # ¡Este órden queda muy importante!
    cls_ramas = [EcsDecai, EcsMortalidad]
