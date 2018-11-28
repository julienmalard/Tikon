import numpy as np
from warnings import warn as avisar


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
    def __init__(símismo, trz, pesos):
        símismo.trz = trz
        símismo.pesos = pesos

    def obt_vals(símismo, n):
        reemplazar = n > len(símismo.trz)
        if reemplazar:
            avisar()
        return np.random.choice(símismo.trz, n, replace=reemplazar, p=símismo.pesos)


class DistCalib(Dist):
    def __init__(símismo, tmñ_trz, val):
        símismo._traza = np.full(tmñ_trz, val)
        símismo.val = val
        símismo.pesos = None

    def agregar_pnt(símismo, val, i):
        trnsf = símismo._transf(val)
        símismo.val = trnsf
        símismo._traza[i] = trnsf

    def gen_traza(símismo):
        return DistTraza(símismo._traza, pesos=símismo.pesos)

    def _transf(símismo, vals):
        pass

    def __float__(símismo):
        return símismo.val
