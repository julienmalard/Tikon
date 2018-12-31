import numpy as np


class Matriz(object):
    def __init__(símismo, mód, var, dims, tiempo=None):

        símismo.mód = mód
        símismo.var = var
        símismo._dims = dims
        símismo.tiempo = tiempo
        símismo._matr = np.zeros(dims.frm())
        if tiempo:
            símismo._matr_t = np.zeros((tiempo.n_pasos(), *dims.frm()))
        else:
            símismo._matr_t = None

    def poner_valor(símismo, vals, rel=False, índs=None):
        if índs is None:
            if rel:
                símismo._matr[:] += vals
            else:
                símismo._matr[:] = vals
        else:
            if rel:
                símismo._matr[símismo._rebanar(índs)] += vals
            else:
                símismo._matr[símismo._rebanar(índs)] = vals

    def _rebanar(símismo, índs):
        return símismo._dims.rebanar(índs)

    def reinic(símismo):
        símismo._matr[:] = 0
        if símismo.tiempo:
            símismo._matr_t[:] = 0

    def í_eje(símismo, eje):
        return símismo._dims.í_eje(eje)

    def n_ejes(símismo):
        return símismo._dims.n_ejes()

    def __str__(símismo):
        return '{}: {}'.format(símismo.mód, símismo.var)
