import numpy as np
import pandas as pd
import xarray as xr


class PruebaCond(object):
    def __call__(símismo, x):
        raise NotImplementedError


class SuperiorOIgual(PruebaCond):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return np.greater_equal(x, símismo.v)


class InferiorOIgual(PruebaCond):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return np.less_equal(x, símismo.v)


class Superior(PruebaCond):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return np.greater(x, símismo.v)


class Inferior(PruebaCond):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return np.less(x, símismo.v)


class Igual(PruebaCond):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return np.equal(x, símismo.v)


class EntreInclusivo(PruebaCond):
    def __init__(símismo, mín, máx):
        símismo.líms = (mín, máx)

    def __call__(símismo, x):
        (mín, máx) = símismo.líms

        return np.logical_and(np.less_equal(x, máx), np.greater_equal(x, mín))


class EntreExclusivo(PruebaCond):
    def __init__(símismo, mín, máx):
        símismo.líms = (mín, máx)

    def __call__(símismo, x):
        (mín, máx) = símismo.líms

        return np.logical_and(np.less(x, máx), np.greater(x, mín))


class Incluye(PruebaCond):
    def __init__(símismo, lista):
        símismo.lista = lista

    def __call__(símismo, x):
        return np.isin(x, símismo.lista)


class Cada(PruebaCond):
    def __init__(símismo, cada):
        símismo.cada = cada

    def __call__(símismo, x):
        return np.equal(np.mod(x, símismo.cada), 0)


class Condición(object):

    def __call__(símismo, sim, paso, f):
        raise NotImplementedError

    def requísitos(símismo, controles=False):
        pass


class CondY(Condición):
    def __init__(símismo, conds):
        símismo.conds = conds

    def __call__(símismo, sim, paso, f):
        return np.logical_and.reduce([c(sim, paso, f) for c in símismo.conds])

    def requísitos(símismo, controles=False):
        return {req for c in símismo.conds for req in (c.requísitos(controles) or {})}


class CondO(Condición):
    def __init__(símismo, conds):
        símismo.conds = conds

    def __call__(símismo, sim, paso, f):
        return np.logical_or.reduce([c(sim, paso, f) for c in símismo.conds])

    def requísitos(símismo, controles=False):
        return {req for c in símismo.conds for req in (c.requísitos(controles) or {})}


class CondFecha(Condición):
    def __init__(símismo, umbral, prueba=Igual):
        símismo.umbral = pd.Timestamp(umbral)
        símismo.prueba = prueba(umbral)

    def __call__(símismo, sim, paso, f):
        return símismo.prueba(f)


class CondDía(Condición):
    def __init__(símismo, umbral, prueba=Igual):
        símismo.umbral = umbral
        símismo.prueba = prueba(umbral)

    def __call__(símismo, sim, paso, f):
        n_día = sim.t.n_día
        return símismo.prueba(n_día)


class CondCada(CondDía):
    def __init__(símismo, cada):
        super().__init__(umbral=cada, prueba=Cada)


class CondVariable(Condición):
    def __init__(símismo, mód, var, prueba, espera, func=xr.DataArray.sum, coords=None):
        símismo.mód = mód
        símismo.var = var
        símismo.prueba = prueba
        símismo.func = func
        símismo.coords = coords or {}
        símismo.espera = espera
        símismo.mem = None

    def __call__(símismo, sim, paso, f):
        val_var = símismo.func(
            sim[símismo.mód].obt_valor(símismo.var).loc[símismo.coords], dim=list(símismo.coords)
        )
        cond_verdad = símismo.prueba(val_var)

        if símismo.mem is None:
            símismo.mem = xr.full_like(cond_verdad, 0, dtype='int')
        listos = np.logical_or(np.greater_equal(símismo.mem, símismo.espera), np.equal(símismo.mem, 0))

        final = np.logical_and(listos, cond_verdad)
        símismo.mem = símismo.mem.where(símismo.mem == 0, símismo.mem + 1)
        símismo.mem = símismo.mem.where(~final, 1)

        return final
