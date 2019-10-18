from tikon.estruc.módulo import Módulo


class Cultivo(Módulo):
    def __init__(símismo, modelos):
        símismo.modelos = modelos
        super().__init__()

    def incrementar(símismo):
        pass

    def cerrar(símismo):
        pass

    def _gen_resultados(símismo, n_rep_estoc, n_rep_parám, vars_interés):
        return


class ModeloCultivo(object):
    pass
