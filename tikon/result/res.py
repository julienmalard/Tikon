import numpy as np

from tikon.estruc.tiempo import EjeTiempo
from tikon.valid.valid import reps_necesarias
from ._matr import Matriz, MatrizTiempo


class Resultado(Matriz):
    def __init__(símismo, nombre, dims, tiempo=None, obs=None):
        super().__init__(dims)
        símismo.nombre = nombre

        if tiempo:
            símismo.matr_t = MatrizTiempo(dims, tiempo.eje)
        else:
            símismo.matr_t = None

        símismo.tiempo = tiempo
        símismo.obs = obs

    def actualizar(símismo):
        if símismo.tiempo:
            rebano = símismo.matr_t.rebanar({'tiempo': símismo.tiempo.día()})
            símismo.matr_t[rebano] = símismo._matr.obt_valor()

    def reinic(símismo):
        if símismo.matr_t is not None:
            símismo.matr_t.reinic()

        super().reinic()

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
        return np.interp(índs, xp=días_act, fp=símismo.matr_t, left=np.nan, right=np.nan)

    def graficar(símismo):
        if not símismo.tiempo:
            raise ValueError('Resultados no temporales no se pueden dibujar.')
        raise NotImplementedError

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        matr = símismo.matr_t or símismo
        return reps_necesarias(
            matr.obt_valor(), eje_parám=matr.í_eje('parám'), eje_estoc=matr.í_eje('estoc'),
            frac_incert=frac_incert, confianza=confianza
        )

    def __str__(símismo):
        return símismo.nombre
