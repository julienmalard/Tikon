from tikon.estruc.módulo import Módulo


class Clima(Módulo):
    nombre = 'clima'

    def __init__(símismo, fuentes=None, escenario=8.5):
        símismo.fuentes = fuentes
        símismo.escenario = escenario
        super().__init__()

    def inter(símismo, coso, tipo):
        pass

    def incrementar(símismo):
        pass

    def cerrar(símismo):
        pass

    def paráms(símismo):
        return []

    def reqs_externos(símismo):
        pass

    def _gen_resultados(símismo, n_rep_estoc, n_rep_parám, vars_interés):
        return
