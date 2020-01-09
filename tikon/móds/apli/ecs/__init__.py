from tikon.ecs import ÁrbolEcs

from .descomp import EcsDescomp
from .mrtld import EcsMortalidad


class EcsProducto(ÁrbolEcs):
    nombre = 'producto'

    # ¡Este órden queda muy importante!
    cls_ramas = [EcsDescomp, EcsMortalidad]
