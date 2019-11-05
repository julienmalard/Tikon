from tikon.ecs import ÁrbolEcs

from .descop import Ecsdescop
from .mrtld import EcsMortalidad


class EcsProducto(ÁrbolEcs):
    nombre = 'producto'

    # ¡Este órden queda muy importante!
    cls_ramas = [Ecsdescop, EcsMortalidad]
