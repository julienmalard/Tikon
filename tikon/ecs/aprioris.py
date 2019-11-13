from .dists import DistAnalítica
from .dists import líms_dist
from .utils import líms_compat


class APriori(object):
    def dist(símismo, líms):
        raise NotImplementedError


class APrioriDens(APriori):
    def __init__(símismo, rango, certidumbre):
        símismo.rango = rango
        símismo.cert = certidumbre

    def dist(símismo, líms):
        return DistAnalítica.de_dens(símismo.cert, símismo.rango, líms=líms)


class APrioriDist(APriori):
    def __init__(símismo, dist):
        símismo._dist = dist
        if isinstance(dist, DistAnalítica):
            símismo._líms_dist = dist.líms
        else:
            símismo._líms_dist = líms_dist(dist)

    def dist(símismo, líms):
        líms_compat(símismo._líms_dist, líms)

        return símismo._dist if isinstance(símismo._dist, DistAnalítica) else DistAnalítica(símismo._dist)
