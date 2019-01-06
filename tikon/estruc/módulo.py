from tikon.ecs import ÁrbolEcs
from tikon.result.dims import Coord, Dims
from tikon.result.res import Resultado


class Módulo(object):
    nombre = NotImplemented

    def __init__(símismo):
        símismo.resultados = None
        símismo.tiempo = None
        símismo.mnjdr_móds = None
        símismo._ecs_simul = None  # type: ÁrbolEcs

    def iniciar_estruc(símismo, tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc):
        símismo.tiempo = tiempo
        símismo.mnjdr_móds = mnjdr_móds

        temporales = []  # para hacer
        obs = símismo.mnjdr_móds.exper.obtener_obs(símismo)

        dims = {
            res: DimsRes(n_estoc=n_rep_estoc, n_parám=n_rep_parám, parc=parc, coords=coords)
            for res, coords in símismo._coords_resultados().items()
        }

        símismo.resultados = ResultadosMódulo(
            [
                Resultado(nmbre, dim, tiempo if nmbre in temporales else None)
                for nmbre, dim in dims.items() if dim.tmñ()
            ]
        )

    def obt_res(símismo, var):
        return símismo.resultados[var]

    def obt_valor(símismo, var):
        return símismo.obt_res(var).obt_valor()

    def poner_valor(símismo, var, valor, rel=False, índs=None):
        símismo.obt_res(var).poner_valor(valor, rel=rel, índs=índs)

    def obt_val_extern(símismo, var, mód):
        símismo.mnjdr_móds.obt_valor(var, mód)

    def obt_val_control(símismo, var):
        return símismo.mnjdr_móds.obt_val_control(var)

    def act_coefs(símismo):
        if símismo._ecs_simul is not None:
            símismo._ecs_simul.act_vals()

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

    def inter(símismo, coso, tipo):
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

    def actualizar(símismo):
        for r in símismo:
            r.actualizar()

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        return {nmbr: res.reps_necesarias(frac_incert, confianza) for nmbr, res in símismo._resultados.items()}

    def __getitem__(símismo, itema):
        return símismo._resultados[str(itema)]

    def __iter__(símismo):
        for r in símismo._resultados.values():
            yield r


class DimsRes(Dims):
    def __init__(símismo, n_estoc, n_parám, parc, coords=None):
        if coords is None:
            coords = {}

        coords = {
            'parc': Coord(parc),
            'estoc': Coord(n_estoc),
            'parám': Coord(n_parám),
            **{crd: Coord(índs) for crd, índs in coords.items()}
        }
        super().__init__(coords=coords)
