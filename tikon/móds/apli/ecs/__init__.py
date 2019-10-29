from tikon.ecs import ÁrbolEcs
from .decomp import EcsDecomp


class EcsProducto(ÁrbolEcs):
    nombre = 'producto'

    # ¡Este órden queda muy importante!
    cls_ramas = [EcsDecomp]
