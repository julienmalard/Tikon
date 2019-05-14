import numpy as np


class Acción(object):
    def __call__(símismo, mnjdr, reps):
        raise NotImplementedError


class AgregarPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def __call__(símismo, mnjdr, reps):
        cambio = np.where(reps, símismo.valor, 0)
        mnjdr['red'].agregar_pobs(pobs=cambio, etapas=símismo.etapa)


class PonerPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def __call__(símismo, mnjdr, reps):
        pobs = mnjdr.obt_valor(mód='red', var='Pobs', índs={'etapa': símismo.etapa})
        cambio = np.where(reps, símismo.valor - pobs, 0)
        mnjdr['red'].ajustar_pobs(pobs=cambio, etapas=símismo.etapa)


class MultPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def __call__(símismo, mnjdr, reps):
        pobs = mnjdr.obt_valor(mód='red', var='Pobs', índs={'etapa': símismo.etapa})
        cambio = np.where(reps, pobs * (símismo.valor - 1), 0)
        mnjdr['red'].ajustar_pobs(pobs=cambio, etapas=símismo.etapa)
