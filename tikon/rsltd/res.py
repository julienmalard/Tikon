import numpy as np

from tikon.tiempo import EjeTiempo


class Resultado(object):
    def __init__(símismo, nombre, dims):
        símismo.nombre = nombre
        símismo._dims = dims
        símismo._matr = np.zeros(dims.frm())

    def poner_valor(símismo, vals, rel=False, índs=None, eje=None):
        if índs is None:
            if rel:
                símismo._matr[:] += vals
            else:
                símismo._matr[:] = vals
        else:
            if rel:
                símismo._matr[símismo._rebanar(índs, eje)] += vals
            else:
                símismo._matr[símismo._rebanar(índs, eje)] = vals

    def obt_valor(símismo, índs=None, eje=None):
        if índs is None:
            return símismo._matr
        else:
            return símismo._matr[símismo._rebanar(índs, eje)]

    def sumar(símismo, eje):
        í_eje = símismo._dims.í_eje(eje)
        return símismo._matr.sum(axis=í_eje)

    def reinic(símismo):
        símismo._matr[:] = 0

    def í_eje(símismo, eje):
        return símismo._dims.í_eje(eje)

    def _rebanar(símismo, índs, eje):
        return tuple([slice(None)] * símismo.í_eje(eje) + [índs])


class ResultadoTemporal(Resultado):
    def __init__(símismo, nombre, dims, tiempo, obs=None):
        super().__init__(dims, nombre)

        símismo.tiempo = tiempo
        símismo.obs = obs
        símismo._matr_t = np.zeros((tiempo.n_pasos(), *dims.frm()))

    def actualizar(símismo):
        símismo._matr_t[símismo.tiempo.día()] = símismo._matr

    def validar(símismo, método):
        if símismo.obs is None:
            raise ValueError('Se necesitan observaciones para validar resultados.')
        vals_res = símismo.obt_valor_t(símismo.obs.tiempo)
        vals_obs = símismo.obs.datos

        return método(vals_res, vals_obs)

    def obt_valor_t(símismo, t):
        if not isinstance(t, EjeTiempo):
            t = EjeTiempo(días=t)

        días_act = símismo.tiempo.eje.días
        índs = símismo.tiempo.índices(t)
        return np.interp(índs, xp=días_act, fp=símismo._matr_t, left=np.nan, right=np.nan)

    def reinic(símismo):
        símismo._matr_t[:] = 0
        super().reinic()

    def graficar(símismo):
        raise NotImplementedError


class Obs(object):
    def __init__(símismo, datos, eje_tiempo):
        símismo.datos = datos
        símismo.tiempo = eje_tiempo


class Dims(object):
    def __init__(símismo, n_estoc, n_parám, parc, coords=None):
        if coords is None:
            coords = {}

        símismo._coords = {
            'parc': Coord(parc),
            'estoc': Coord(n_estoc),
            'parám': Coord(n_parám),
            **{crd: Coord(índs) for crd, índs in coords.items()}}

        símismo._frm = tuple(crd.tmñ() for crd in símismo._coords.values())

    def frm(símismo):
        return símismo._frm

    def í_eje(símismo, eje):
        return next(i for i, crd in enumerate(símismo._coords) if crd == eje)


class Coord(object):
    def __init__(símismo, índs):
        símismo.índs = índs

    def tmñ(símismo):
        if isinstance(símismo.índs, int):
            return símismo.índs
        else:
            return len(símismo.índs)
