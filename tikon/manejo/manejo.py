from tikon.estruc.módulo import Módulo


class Manejo(Módulo):
    nombre = 'manejo'

    def __init__(símismo, reglas=None):
        símismo.reglas = reglas or []

        super().__init__()

    def incrementar(símismo):
        for r in símismo:
            r(símismo.mnjdr_móds, símismo.tiempo)

    def cerrar(símismo):
        pass

    def paráms(símismo, módulos):
        return []

    def reqs_externos(símismo):
        pass

    def _gen_resultados(símismo, n_rep_estoc, n_rep_parám, vars_interés):
        return

    def __iter__(símismo):
        for r in símismo.reglas:
            yield r


class Regla(object):
    def __init__(símismo, condición, acción):
        símismo.condición = condición
        símismo.acción = acción

    def __call__(símismo, mnjdr, tiempo):
        if símismo.condición(mnjdr, tiempo):
            símismo.acción(mnjdr)
