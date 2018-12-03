import numpy as np


class EcsSimul(object):
    def __init__(símismo, etapas, calibs, n_rep_paráms):

        símismo._categs = {str(ctg): ctg for ctg in árbol_ecs}

    def __getitem__(símismo, itema):
        return símismo._categs[itema]


class CategEcsSimul(object):
    def __init__(símismo, subcategs):
        símismo._subcategs = {str(sub): sub for sub in subcategs}

    def evaluar(símismo, paso):
        for sub in símismo._subcategs.values():
            sub.evaluar(paso)

    def __getitem__(símismo, itema):
        return símismo._subcategs[itema]


class SubCategEcsSimul(object):
    def __init__(símismo, ecs, res):
        símismo._ecs = ecs
        símismo._res = res

    def evaluar(símismo, paso):
        for ec in símismo._ecs:
            ec.evaluar(paso, res=símismo._res)


class EcSimul(object):
    def __init__(símismo, func, paráms, í_etapas):
        símismo.func = func
        símismo.paráms = paráms
        símismo.í_etapas = í_etapas

    def evaluar(símismo, paso, res):
        val = símismo.func(paráms=símismo.paráms, paso=paso, mód=mód)
        res.poner_val(val, símismo.í_etapas)


class ParámsEc(object):
    def __init__(símismo, paráms):

class MatrValoresParám(object):
    def __init__(símismo, dists):
        símismo.dists = dists
        símismo.vals = np.array(dists, dtype=float)

    def __float__(símismo):
        símismo.vals[:] = símismo.dists
        return símismo.vals
