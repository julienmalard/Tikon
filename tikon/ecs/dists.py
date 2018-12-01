import numpy as np
from warnings import warn as avisar


class Dist(object):
    def obt_vals(símismo, n):
        raise NotImplementedError


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
        return ValoresDist(np.random.choice(símismo.trz, n, replace=reemplazar, p=símismo.pesos))


class DistCalib(Dist):
    def __init__(símismo, tmñ_trz):
        símismo._traza = np.full(tmñ_trz, 0)
        símismo.val = 0

    def agregar_pnt(símismo, val, i):
        trnsf = símismo._transf(val)
        símismo.val = trnsf
        símismo._traza[i] = trnsf

    def gen_traza(símismo, buenas, pesos):
        return DistTraza(símismo._traza[buenas], pesos=pesos)

    def _transf(símismo, vals):
        pass

    def obt_vals(símismo, n):
        if n != 1:
            raise ValueError
        return ValoresDistCalib(símismo)

    def __float__(símismo):
        return símismo.val




class ValoresDist(object):
    def __init__(símismo, vals):
        símismo.vals = vals

    def __float__(símismo):
        return símismo.vals


class ValoresDistCalib(ValoresDist):
    def __index__(símismo, dist_calib):
        símismo.dist = dist_calib
        vals = float(símismo.dist)
        super().__init__(vals)

    def __float__(símismo):
        símismo.vals[:] = float(símismo.dist)
        return super().__float__()
