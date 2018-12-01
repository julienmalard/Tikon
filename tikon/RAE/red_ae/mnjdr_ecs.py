import numpy as np


class EcsSimul(object):
    def __init__(símismo, árbol_ecs):
        símismo._categs = {str(ctg): ctg for ctg in árbol_ecs}

    def iniciar(símismo, etapas, n_rep_paráms):
        for categ in símismo:
            for sub in categ:
                categ.iniciar(etapas, n_rep_paráms)

    def __getitem__(símismo, itema):
        return símismo._categs[itema]


class CategEcsSimul(object):
    def __init__(símismo, subcategs):
        símismo._subcategs = {str(sub): sub for sub in subcategs}

    def __getitem__(símismo, itema):
        return símismo._subcategs[itema]


class SubCategEcsSimul(object):
    def __init__(símismo, ecs):
        símismo._ecs = {str(ec): ec for ec in ecs}

    def __getitem__(símismo, itema):
        return símismo._ecs[itema]


class EcSimul(object):
    def __init__(símismo, func, paráms):
        símismo.func = func
        símismo.paráms = paráms

    def evaluar(símismo, paso, mód):
        símismo.func(paráms=símismo.paráms, paso=paso, mód=mód)


class ParámsEc(object):
    def __init__(símismo, paráms):

class MatrValoresParám(object):
    def __init__(símismo, dists):
        símismo.dists = dists
        símismo.vals = np.array(dists, dtype=float)

    def __float__(símismo):
        símismo.vals[:] = símismo.dists
        return símismo.vals
