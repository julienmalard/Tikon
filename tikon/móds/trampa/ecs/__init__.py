from tikon.ecs import ÁrbolEcs

from .descomp import EcsDescomp
from .captura import EcsCaptura


class EcsTrampa(ÁrbolEcs):
    nombre = 'trampa'

    # ¡Este órden queda muy importante!
    cls_ramas = [EcsDescomp, EcsCaptura]
