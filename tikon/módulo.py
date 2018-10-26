class Módulo(object):
    def __init__(símismo):
        símismo.resultados = {}

    def iniciar(símismo, días, f_inic, paso, n_rep_estoc, n_rep_parám):

        í_pasos = range(0, paso*n_pasos, paso)
        símismo.resultados = símismo._gen_resultados(
            í_pasos, n_rep_estoc=n_rep_estoc, n_rep_parám=n_rep_parám, n_parc=n_parc
        )

    def incrementar(símismo, paso):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError

    def _gen_resultados(símismo, í_pasos, n_rep_estoc, n_rep_parám, n_parc):
        raise NotImplementedError

    def _gen_obs(símismo):
        raise NotImplementedError

    def calc_valid(símismo):
        for res in símismo.resultados.items():
            res.validar()

