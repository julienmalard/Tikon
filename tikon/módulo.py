from tikon.rsltd.res import Dims, Resultado, ResultadoTemporal


class Módulo(object):
    nombre = NotImplemented

    def __init__(símismo):
        símismo.resultados = None
        símismo.tiempo = None
        símismo.mnjdr_móds = None

    def iniciar_estruc(símismo, tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc):
        símismo.tiempo = tiempo
        símismo.mnjdr_móds = mnjdr_móds


        temporales = []  # para hacer
        obs = []

        dims = {
            res: Dims(n_estoc=n_rep_estoc, n_parám=n_rep_parám, parc=parc, coords=coords)
            for res, coords in símismo._coords_resultados().items()
        }

        símismo.resultados = ResultadosMódulo(
            [
                ResultadoTemporal(nmbre, dim, tiempo) if nmbre in temporales else Resultado(nmbre, dim)
                for nmbre, dim in dims.items() if dim.tmñ()
            ]
        )

    def obt_valor(símismo, var):
        return símismo.resultados[var].obt_valor()

    def poner_valor(símismo, var, valor, rel=False):
        símismo.resultados[var].poner_valor(valor, rel=rel)

    def obt_val_extern(símismo, var, mód):
        símismo.mnjdr_móds.obt_valor(var, mód)

    def obt_val_control(símismo, var):
        return símismo.mnjdr_móds.obt_val_control(var)

    def iniciar_vals(símismo):
        raise NotImplementedError

    def incrementar(símismo):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError

    def paráms(símismo):
        raise NotImplementedError

    def reqs_externos(símismo):
        raise NotImplementedError

    def _coords_resultados(símismo):
        raise NotImplementedError

    def calc_valid(símismo):
        for res in símismo.resultados.items():
            res.validar()

    def __str__(símismo):
        return símismo.nombre


class ResultadosMódulo(object):
    def __init__(símismo, resultados):
        símismo._resultados = {str(res): res for res in resultados}

    def reinic(símismo):
        for r in símismo:
            r.reinic()

    def __getitem__(símismo, itema):
        return símismo._resultados[str(itema)]
