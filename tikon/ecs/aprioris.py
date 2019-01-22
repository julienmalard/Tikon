from ._espec_dists import líms_dist, obt_nombre
from ._utils import proc_líms, líms_compat
from .dists import DistAnalítica


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
        símismo._líms_dist = líms_dist(obt_nombre(dist))

    def dist(símismo, líms):
        líms = proc_líms(líms)
        líms_compat(líms, símismo._líms_dist)

        return símismo._dist
