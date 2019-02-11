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

    def obt_valor(símismo, var, índs=None):
        return símismo.obt_res(var).obt_valor(índs=índs)

    def poner_valor(símismo, var, valor, rel=False, índs=None):
        símismo.obt_res(var).poner_valor(valor, rel=rel, índs=índs)

    def obt_val_extern(símismo, var, mód):
        return símismo.mnjdr_móds.obt_valor(var, mód)

    def obt_val_control(símismo, var):
        return símismo.mnjdr_móds.obt_val_control(var)

    def act_coefs(símismo):
        if símismo._ecs_simul is not None:
            símismo._ecs_simul.act_vals()

    def iniciar_vals(símismo):
        if símismo.resultados:  # para hacer: más elegante
            símismo.resultados.reinic()

    def incrementar(símismo):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError

    def paráms(símismo, módulos):
        raise NotImplementedError

    def reqs_externos(símismo):
        raise NotImplementedError

    def inter(símismo, coso, tipo):
        raise NotImplementedError

    def _gen_resultados(símismo, n_rep_estoc, n_rep_parám, vars_interés):
        raise NotImplementedError

    def guardar_calib(símismo, directorio=''):
        pass  # para hacer: genérico

    def __str__(símismo):
        return símismo.nombre


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
