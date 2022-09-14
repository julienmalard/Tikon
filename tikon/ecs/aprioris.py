from typing import Optional

from numpy.typing import ArrayLike
from scipy.stats._distn_infrastructure import rv_continuous_frozen

from .dists import DistAnalítica
from .dists import líms_dist
from .dists.utils import Líms_Con_None
from .utils import líms_compat
from ..tipos import Tipo_Valor_Numérico


class APriori(object):
    def dist(símismo, líms: Optional[Líms_Con_None]) -> DistAnalítica:
        raise NotImplementedError


class APrioriDens(APriori):
    def __init__(símismo, rango: Optional[Líms_Con_None], certidumbre: Tipo_Valor_Numérico):
        símismo.rango = rango
        símismo.cert = certidumbre

    def dist(símismo, líms: Optional[Líms_Con_None]) -> DistAnalítica:
        return DistAnalítica.de_dens(símismo.cert, símismo.rango, líms=líms)


class APrioriDist(APriori):
    def __init__(símismo, dist: DistAnalítica | str | rv_continuous_frozen):
        símismo._dist = dist
        if isinstance(dist, DistAnalítica):
            símismo._líms_dist = dist.líms
        else:
            símismo._líms_dist = líms_dist(dist)

    def dist(símismo, líms: Optional[Líms_Con_None]) -> DistAnalítica:
        líms_compat(símismo._líms_dist, líms)

        return símismo._dist if isinstance(símismo._dist, DistAnalítica) else DistAnalítica(símismo._dist)
