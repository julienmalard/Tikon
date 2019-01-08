import numpy as np

from tikon.result.dibujar import graficar_pred
from tikon.result.valid import reps_necesarias, validar_matr_pred
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
        if símismo.matr_t:
            símismo.matr_t.poner_valor(símismo._matr, índs={'días': [símismo.tiempo.día()]})

    def reinic(símismo):
        if símismo.matr_t is not None:
            símismo.matr_t.reinic()

        super().reinic()

    def validar(símismo):
        if símismo.matr_t is not None and símismo.obs is not None:
            d_valid = {}
            for índs in símismo.obs.iter_índs(excluir='días'):
                matr_t = símismo.matr_t
                ejes_orig = np.argsort([matr_t.í_eje('días'), matr_t.í_eje('estoc'), matr_t.í_eje('parám')])

                vals_res = símismo.obt_valor_t(símismo.obs.eje_tiempo, índs=índs)
                vals_res = np.moveaxis(vals_res, ejes_orig, [0, 1, 2])
                vals_res = vals_res.reshape(vals_res.shape[:3])
                vals_obs = símismo.obs.obt_valor(índs).squeeze()

                dic = d_valid
                l_llaves = list(str(ll) for ll in índs.values())
                for ll in l_llaves[:-1]:
                    if ll not in dic:
                        dic[ll] = {}
                        dic = dic[ll]
                dic[l_llaves[-1]] = validar_matr_pred(vals_res, vals_obs)
            return d_valid

    def obt_valor_t(símismo, t, índs=None):
        if símismo.matr_t is None:
            raise ValueError('Resultados no temporales no pueden dar datos temporales.')
        return símismo.matr_t.obt_val_t(t, índs=índs)

    def graficar(símismo, directorio=''):
        if símismo.matr_t:
            matr_t = símismo.matr_t
            for índs in matr_t.iter_índs(excluir=['días', 'estoc', 'parám']):
                ord_ejes = np.argsort([matr_t.í_eje('días'), matr_t.í_eje('estoc'), matr_t.í_eje('parám')])

                vals_res = símismo.obt_valor_t(símismo.tiempo.eje.eje(), índs=índs)
                vals_res = np.moveaxis(vals_res, ord_ejes, [0, 1, 2])
                try:
                    vals_obs = símismo.obs.obt_valor(índs)
                    eje_obs = símismo.obs.eje_tiempo.eje()
                except (ValueError, AttributeError):  # para hacer: más elegante
                    vals_obs = eje_obs = None

                título = ', '.join(ll + ' ' + str(v) for ll, v in índs.items())

                graficar_pred(
                    título, directorio,
                    vals_res, t_pred=símismo.tiempo.eje.eje(), t_obs=eje_obs, vector_obs=vals_obs,
                )

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        matr = símismo.matr_t or símismo
        return reps_necesarias(
            matr.obt_valor(), eje_parám=matr.í_eje('parám'), eje_estoc=matr.í_eje('estoc'),
            frac_incert=frac_incert, confianza=confianza
        )

    def finalizar(símismo):
        pass

    def __str__(símismo):
        return símismo.nombre
