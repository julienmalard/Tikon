import numpy as np


class Dist(object):
    pass


class DistAnalítica(Dist):
    def __init__(símismo, dist, paráms):
        pass

    @classmethod
    def de_líms(cls, líms):
        return DistAnalítica()

    @classmethod
    def de_dens(cls, dens, líms_dens, líms):
        return DistAnalítica()


class DistTraza(Dist):
    def __init__(símismo, trz):
        símismo.trz = trz


class DistCalib(Dist):
    def __init__(símismo, tmñ, val):
        símismo._traza = np.full(tmñ, val)
        símismo.val = val

    def agregar_pnt(símismo, val, i):
        símismo.val = val
        símismo._traza[i] = val

    def gen_traza(símismo):
        return DistTraza(símismo._traza)

    def __float__(símismo):
        return símismo.val
