from tikon.ecs import ÁrbolEcs

from .decomp import EcsDecomp
from .mrtld import EcsMortalidad


class EcsProducto(ÁrbolEcs):
    nombre = 'producto'

    # ¡Este órden queda muy importante!
    cls_ramas = [EcsDecomp, EcsMortalidad]
