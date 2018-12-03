import numpy as np

from tikon.tiempo import EjeTiempo


class Resultado(object):
    def __init__(símismo, dims):
        símismo.dims = dims
        símismo.matr = np.zeros(dims.frm())

    def poner_valor(símismo, vals, rel=False, índs=None, eje=None):
        if índs is None:
            if rel:
                símismo.matr[:] += vals
            else:
                símismo.matr[:] = vals
        else:
            if rel:
                símismo.matr[símismo.rebanar(índs, eje)] += vals
            else:
                símismo.matr[símismo.rebanar(índs, eje)] = vals

    def obt_valor(símismo, índs=None, eje=None):
        if índs is None:
            return símismo.matr
        else:
            return símismo.matr[símismo.rebanar(índs, eje)]

    def sumar(símismo, eje):
        í_eje = símismo.dims.í_eje(eje)
        return símismo.matr.sum(axis=í_eje)

    def rebanar(símismo, índs, eje):
        í_eje = símismo.dims.í_eje(eje)

        return tuple([slice(None)]*í_eje + [índs])


class ResultadoTemporal(Resultado):
    def __init__(símismo, nombre, dims, tiempo, obs=None):
        super().__init__(dims)

        símismo.nombre = nombre
        símismo.tiempo = tiempo
        símismo.obs = obs
        símismo.matr_t = np.zeros((tiempo.n_pasos(), *dims.frm()))

    def actualizar(símismo):
        símismo.matr_t[símismo.tiempo.día()] = símismo.matr

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
        return np.interp(índs, xp=días_act, fp=símismo.matr_t, left=np.nan, right=np.nan)

    def graficar(símismo):
        pass


class Obs(object):
    def __init__(símismo, datos, eje_tiempo):
        símismo.datos = datos
        símismo.tiempo = eje_tiempo


class Dims(object):
    def __init__(símismo, n_estoc, n_parám, n_parc, coords=None):
        if coords is None:
            coords = {}
        símismo._frm = (n_parc, n_estoc, n_parám, *coords.values())
        símismo.coords = coords

    def frm(símismo):
        return símismo._frm


class Coords(object):
    def __init__(símismo, nombre):
