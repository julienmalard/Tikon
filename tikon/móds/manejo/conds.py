import numpy as np
import pandas as pd
from frozendict import frozendict

from tikon.datos.datos import Datos, lleno_como, f_numpy as fnp


class PruebaCond(object):
    def __call__(símismo, x):
        raise NotImplementedError


class SuperiorOIgual(PruebaCond):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return fnp(np.greater_equal, x, símismo.v)


class InferiorOIgual(PruebaCond):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return fnp(np.less_equal, x, símismo.v)


class Superior(PruebaCond):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return fnp(np.greater, x, símismo.v)


class Inferior(PruebaCond):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return fnp(np.less, x, símismo.v)


class Igual(PruebaCond):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return fnp(np.equal, x, símismo.v)


class EntreInclusivo(PruebaCond):
    def __init__(símismo, mín, máx):
        símismo.líms = (mín, máx)

    def __call__(símismo, x):
        (mín, máx) = símismo.líms

        return fnp(np.logical_and, fnp(np.less_equal, x, máx), fnp(np.greater_equal, x, mín))


class EntreExclusivo(PruebaCond):
    def __init__(símismo, mín, máx):
        símismo.líms = (mín, máx)

    def __call__(símismo, x):
        (mín, máx) = símismo.líms

        return fnp(np.logical_and, fnp(np.less, x, máx), fnp(np.greater, x, mín))


class Incluye(PruebaCond):
    def __init__(símismo, lista):
        símismo.lista = lista

    def __call__(símismo, x):
        return fnp(np.isin, x, símismo.lista)


class Cada(PruebaCond):
    def __init__(símismo, cada):
        símismo.cada = cada

    def __call__(símismo, x):
        return fnp(np.equal, fnp(np.mod, x, símismo.cada), 0)


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
        símismo.prueba = prueba(símismo.umbral)

    def __call__(símismo, sim, paso, f):
        return símismo.prueba(f)


class CondDía(Condición):
    def __init__(símismo, umbral, prueba=Igual):
        símismo.umbral = umbral
        símismo.prueba = prueba(umbral)

    def __call__(símismo, sim, paso, f):
        n_día = sim.t.n_día
        return símismo.prueba(n_día)


class CondCadaDía(Condición):
    def __init__(símismo, cada, desfase=0):
        símismo.cada = cada
        símismo.desfase = desfase
        símismo.prueba = Cada(cada)

    def __call__(símismo, sim, paso, f):
        n_día = sim.t.n_día
        return símismo.prueba(n_día - símismo.desfase)


class CondVariable(Condición):
    def __init__(símismo, mód, var, prueba, espera, func=Datos.suma, coords=None):
        símismo.mód = mód
        símismo.var = var
        símismo.prueba = prueba
        símismo.func = func
        símismo.coords = coords or frozendict({})
        símismo.espera = espera
        símismo.mem = None

    def __call__(símismo, sim, paso, f):
        val_var = símismo.func(
            sim[símismo.mód].obt_valor(símismo.var).loc[símismo.coords], dim=list(símismo.coords)
        )
        cond_verdad = símismo.prueba(val_var)

        if símismo.mem is None:
            símismo.mem = lleno_como(cond_verdad, 0, tipod='int')
        listos = fnp(np.logical_or, fnp(np.greater_equal, símismo.mem, símismo.espera), fnp(np.equal, símismo.mem, 0))

        verdad_final = fnp(np.logical_and, listos, cond_verdad)
        símismo.mem = símismo.mem.donde(símismo.mem == 0, símismo.mem + 1)
        símismo.mem = símismo.mem.donde(~verdad_final, 1)

        return verdad_final
