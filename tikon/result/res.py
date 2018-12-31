import numpy as np

from tikon.estruc.tiempo import EjeTiempo
from ._matr import Matriz
from tikon.valid.valid import reps_necesarias


class Resultado(Matriz):
    def __init__(símismo, nombre, dims, tiempo=None, obs=None):
        super().__init__(nombre, dims=dims, tiempo=tiempo)
        símismo.obs = obs

    def obt_valor(símismo, índs=None):
        if índs is None:
            return símismo._matr
        else:
            return símismo._matr[símismo._rebanar(índs)]

    def sumar(símismo, eje):
        í_eje = símismo._dims.í_eje(eje)
        return símismo._matr.sum(axis=í_eje)

    def actualizar(símismo):
        if símismo.tiempo:
            símismo._matr_t[símismo.tiempo.día()] = símismo._matr

    def validar(símismo, método):
        if símismo.tiempo and símismo.obs:
            vals_res = símismo.obt_valor_t(símismo.obs.tiempo)
            vals_obs = símismo.obs.datos

            return método(vals_res, vals_obs)

    def obt_valor_t(símismo, t):
        if not símismo.tiempo:
            raise ValueError('Resultados no temporales no pueden dar datos temporales.')

        if not isinstance(t, EjeTiempo):
            t = EjeTiempo(días=t)

        días_act = símismo.tiempo.eje.días
        índs = símismo.tiempo.índices(t)
        return np.interp(índs, xp=días_act, fp=símismo._matr_t, left=np.nan, right=np.nan)

    def graficar(símismo):
        if not símismo.tiempo:
            raise ValueError('Resultados no temporales no se pueden dibujar.')
        raise NotImplementedError

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        matr = símismo._matr_t or símismo._matr
        return reps_necesarias(
            matr, eje_parám=símismo.í_eje('parám'), eje_estoc=símismo.í_eje('estoc'),
            frac_incert=frac_incert, confianza=confianza
        )
