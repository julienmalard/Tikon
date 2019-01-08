import os

from tikon.ecs import ÁrbolEcs
from tikon.result.dims import Coord, Dims


class Módulo(object):
    nombre = NotImplemented

    def __init__(símismo):
        símismo.resultados = None
        símismo.tiempo = None
        símismo.mnjdr_móds = None
        símismo._ecs_simul = None  # type: ÁrbolEcs

    def iniciar_estruc(símismo, tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés):
        símismo.tiempo = tiempo
        símismo.mnjdr_móds = mnjdr_móds

        símismo.resultados = símismo._gen_resultados(
            n_rep_estoc=n_rep_estoc, n_rep_parám=n_rep_parám, vars_interés=vars_interés
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

    def _gen_resultados(símismo, n_rep_estoc, n_rep_parám, vars_interés):
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

    def finalizar(símismo):
        for r in símismo:
            r.finalizar()

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        return {nmbr: res.reps_necesarias(frac_incert, confianza) for nmbr, res in símismo._resultados.items()}

    def validar(símismo):
        valid = {nmb: res.validar() for nmb, res in símismo._resultados.items()}
        return {ll: v for ll, v in valid.items() if v}

    def graficar(símismo, directorio):
        for nmb, res in símismo._resultados.items():
            res.graficar(directorio=os.path.join(directorio, nmb))

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
