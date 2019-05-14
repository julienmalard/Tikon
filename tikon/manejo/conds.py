import numpy as np


class SuperiorOIgual(object):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return np.greater_equal(x, símismo.v)


class InferiorOIgual(object):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return np.less_equal(x, símismo.v)


class Superior(object):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return np.greater(x, símismo.v)


class Inferior(object):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return np.less(x, símismo.v)


class Igual(object):
    def __init__(símismo, v):
        símismo.v = v

    def __call__(símismo, x):
        return np.equal(x, símismo.v)


class EntreInclusivo(object):
    def __init__(símismo, mín, máx):
        símismo.líms = (mín, máx)

    def __call__(símismo, x):
        (mín, máx) = símismo.líms

        return np.logical_and(np.less_equal(x, máx), np.greater_equal(x, mín))


class EntreExclusivo(object):
    def __init__(símismo, mín, máx):
        símismo.líms = (mín, máx)

    def __call__(símismo, x):
        (mín, máx) = símismo.líms

        return np.logical_and(np.less(x, máx), np.greater(x, mín))


class Incluye(object):
    def __init__(símismo, lista):
        símismo.lista = lista

    def __call__(símismo, x):
        return np.isin(x, símismo.lista)


class Cada(object):
    def __init__(símismo, cada):
        símismo.cada = cada

    def __call__(símismo, x):
        return np.equal(np.mod(x, símismo.cada), 0)


class Condición(object):

    def __call__(símismo, mnjdr, tiempo):
        raise NotImplementedError


class CondTiempo(Condición):

    def __init__(símismo, umbral, prueba=Igual):
        símismo.umbral = umbral
        símismo.prueba = prueba(umbral)

    def __call__(símismo, mnjdr, tiempo):
        if isinstance(símismo.umbral, int):
            t = tiempo.día()
        else:
            t = tiempo.fecha()  # para hacer: umbrales entre

        return símismo.prueba(t)


class CondCada(Condición):
    def __init__(símismo, cada):
        símismo.cada = cada
        símismo.prueba = Cada(símismo.cada)

    def __call__(símismo, mnjdr, tiempo):
        return símismo.prueba(tiempo.día())


class CondVariable(Condición):
    def __init__(símismo, mód, var, prueba, espera=14, índs=None):
        símismo.mód = mód
        símismo.var = var
        símismo.prueba = prueba
        símismo.índs = [índs] if isinstance(índs, dict) else índs
        símismo.espera = espera
        símismo.mem = None

    def __call__(símismo, mnjdr, tiempo):
        val_var = np.sum([mnjdr.obt_valor(var=símismo.var, mód=símismo.mód, índs=í) for í in símismo.índs], axis=0)
        cond_verdad = símismo.prueba(val_var)

        if símismo.mem is None:
            símismo.mem = np.zeros_like(cond_verdad, dtype=int)
        listo = np.logical_or(np.greater_equal(símismo.mem, símismo.espera), np.equal(símismo.mem, 0))

        final = np.logical_and(listo, cond_verdad)
        símismo.mem[símismo.mem != 0] += 1
        símismo.mem[final] = 1

        return final


class CondPoblación(CondVariable):
    def __init__(símismo, etapa, prueba, espera=14):
        etapas = [etapa] if not isinstance(etapa, list) else etapa
        super().__init__(
            mód='red', var='Pobs', índs=[{'etapa': e} for e in etapas],
            prueba=prueba, espera=espera
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
