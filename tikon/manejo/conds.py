import numpy as np


def superior_o_igual(v):
    return lambda x: np.greater_equal(x, v)


def inferior_o_igual(v):
    return lambda x: np.less_equal(x, v)


def superior(v):
    return lambda x: np.greater(x, v)


def inferior(v):
    return lambda x: np.less(x, v)


def igual(v):
    return lambda x: np.equal(x, v)


def entre_inclusivo(mín, máx):
    return lambda x: np.logical_and(np.less_equal(x, máx), np.greater_equal(x, mín))


def entre_exclusivo(mín, máx):
    return lambda x: np.logical_and(np.less(x, máx), np.greater(x, mín))


def incluye(lista):
    return lambda x: np.isin(x, lista)


def módulo(cada):
    return lambda x: np.equal(np.mod(x, cada), 0)


class Condición(object):

    def __call__(símismo, mnjdr, tiempo):
        raise NotImplementedError


class CondTiempo(Condición):

    def __init__(símismo, umbral, prueba=igual):
        símismo.umbral = umbral
        símismo.prueba = prueba(umbral)

    def __call__(símismo, mnjdr, tiempo):
        if isinstance(símismo.umbral, int):
            t = tiempo.día()
        else:
            t = tiempo.fecha()

        return símismo.prueba(t)


class CondCada(Condición):
    def __init__(símismo, cada):
        símismo.cada = cada
        símismo.prueba = módulo(símismo.cada)

    def __call__(símismo, mnjdr, tiempo):
        return símismo.prueba(tiempo.día())


class CondVariable(Condición):
    def __init__(símismo, mód, var, prueba, índs=None):
        símismo.mód = mód
        símismo.var = var
        símismo.prueba = prueba
        símismo.índs = índs

    def __call__(símismo, mnjdr, tiempo):
        val_var = mnjdr.obt_valor(var=símismo.var, mód=símismo.mód, índs=símismo.índs)
        return símismo.prueba(val_var)


class CondPoblación(CondVariable):
    def __init__(símismo, etapa, prueba):
        super().__init__(
            mód='red', var='Pobs', índs={'etapa': etapa},
            prueba=prueba
        )


class CondY(Condición):
    def __init__(símismo, conds):
        símismo.conds = conds

    def __call__(símismo, mnjdr, tiempo):
        return np.logical_and.reduce([c(mnjdr, tiempo) for c in símismo.conds])


class CondO(Condición):
    def __init__(símismo, conds):
        símismo.conds = conds

    def __call__(símismo, mnjdr, tiempo):
        return np.logical_or.reduce([c(mnjdr, tiempo) for c in símismo.conds])
