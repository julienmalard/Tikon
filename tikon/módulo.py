from tikon.rsltd.res import Dims


class Módulo(object):
    def __init__(símismo):
        símismo.resultados = None
        símismo.tiempo = None
        símismo.conex_móds = None

    def iniciar_estruc(símismo, tiempo, conex_móds, calibs, n_rep_estoc, n_rep_parám):
        símismo.tiempo = tiempo
        símismo.conex_móds = conex_móds

        símismo.resultados = Resultados(
            [
                Resultado(Dims(n_estoc=n_rep_estoc, n_parám=n_rep_parám, n_parc=n_parc, coords=coords))
                for coords in símismo._coords_resultados()
            ]
        )

    def obt_valor(símismo, var):
        return símismo.resultados[var]

    def poner_valor(símismo, var, valor, rel=False):
        símismo.resultados[var].poner_valor(valor, rel=rel)

    def obt_val_extern(símismo, mód, var):
        símismo.conex_móds.obt_valor(mód, var)

    def iniciar_vals(símismo):
        raise NotImplementedError

    def incrementar(símismo, paso):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError

    def paráms(símismo):
        raise NotImplementedError

    def reqs_externos(símismo):
        raise NotImplementedError

    def _coords_resultados(símismo):
        raise NotImplementedError

    def _gen_obs(símismo):
        raise NotImplementedError

    def calc_valid(símismo):
        for res in símismo.resultados.items():
            res.validar()
