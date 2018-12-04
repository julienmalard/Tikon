from warnings import warn as avisar

import numpy as np


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


class MnjdrDists(object):
    def __init__(símismo):
        símismo.val = None
        símismo.índs = {}

    def actualizar(símismo, dist, índs=None):
        if isinstance(índs, str):
            índs = [índs]
        else:
            índs = list(índs)  # generar copia

        if índs is None or not len(índs):
            símismo.val = dist
        else:
            í = índs.pop(0)
            sub_dist = símismo.__class__()
            sub_dist.actualizar(dist, índs)
            símismo.índs[í] = sub_dist

    def obt_val(símismo, índs=None):

        if isinstance(índs, str):
            índs = [índs]
        else:
            índs = list(índs)  # generar copia

        if índs is None or not len(índs):
            return símismo.val
        else:
            í = índs.pop(0)
            if í in símismo.índs:
                return símismo.índs[í].obt_valor(índs)
            else:
                return símismo.val

    def __getitem__(símismo, itema):
        return símismo.índs[itema]


class MnjdrDistsClbs(MnjdrDists):

    def actualizar(símismo, dist, índs=None):
        if not isinstance(dist, DistCalib):
            raise TypeError
        super().actualizar(dist=dist, índs=índs)

    def obt_trazas(símismo, mnjdr=None):
        if mnjdr is None:
            mnjdr = MnjdrDists()
        mnjdr.actualizar(dist=símismo.val.gen_traza())

        for í, mnjdr_í in símismo.índs:
            mnjdr.actualizar(mnjdr_í.obt_trazas(mnjdr=mnjdr), índs=í)

        return mnjdr


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
