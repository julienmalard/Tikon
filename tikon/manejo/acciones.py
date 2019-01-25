class Acción(object):
    def call(símismo, mnjdr):
        raise NotImplementedError


class AgregarPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def call(símismo, mnjdr):
        mnjdr['red'].agregar_pobs(pobs=símismo.valor, etapas=símismo.etapa)


class PonerPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def call(símismo, mnjdr):
        pobs = mnjdr.obt_valor('red', 'Pobs', índs={'etapa': símismo.etapa})
        mnjdr['red'].ajustar_pobs(pobs=símismo.valor - pobs, etapas=símismo.etapa)


class MultPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def call(símismo, mnjdr):
        pobs = mnjdr.obt_valor('red', 'Pobs', índs={'etapa': símismo.etapa})
        mnjdr.poner_valor('red', var='Pobs', val=pobs * (símismo.valor - 1), etapas=símismo.etapa)
