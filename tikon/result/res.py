import os

import numpy as np

from tikon.result.dibujar import graficar_pred
from tikon.result.valid import reps_necesarias, validar_matr_pred, dens_con_pred
from ._matr import Matriz, MatrizTiempo


class Resultado(Matriz):
    def __init__(símismo, nombre, dims, tiempo=None, obs=None):
        super().__init__(dims)
        símismo.nombre = nombre

        if tiempo:
            símismo.matr_t = MatrizTiempo(dims, tiempo.eje)
        else:
            símismo.matr_t = None

        símismo.tiempo = tiempo  # para hacer: ¿combinar tiempo y matr_t?
        símismo.obs = obs

    def actualizar(símismo):
        if símismo.matr_t:
            símismo.matr_t.poner_valor(símismo._matr, índs={'días': [símismo.tiempo.día()]})

    def reinic(símismo):
        super().reinic()

        if símismo.matr_t is not None:
            símismo.matr_t.reinic()

        if símismo.tiempo:
            símismo.tiempo.reinic()

        if símismo.obs:
            t_inic = símismo.tiempo.día()  # para hacer: con f_inic
            dims_obs = símismo.obs.dims

            # para hacer: en una única llamada a poner_valor() en cuanto funcionen los índices múltiples en rebanar()
            for índs in dims_obs.iter_índs(excluir='días'):
                vals_inic = símismo.obs.obt_val_t(t_inic, índs=índs)

                vals_inic[np.isnan(vals_inic)] = 0
                símismo.poner_valor(vals=vals_inic, índs=índs)

            símismo.actualizar()

    def validar(símismo):
        if símismo._validable():
            d_valid = {}
            eje_tiempo = símismo.obs.eje_tiempo.cortar(símismo.tiempo.eje)
            for índs in símismo.obs.iter_índs(excluir='días'):
                matr_t = símismo.matr_t
                ejes_orig = np.argsort([matr_t.í_eje('días'), matr_t.í_eje('estoc'), matr_t.í_eje('parám')])

                vals_res = símismo.obt_valor_t(eje_tiempo, índs=índs)
                vals_res = np.moveaxis(vals_res, ejes_orig, [0, 1, 2])
                vals_res = vals_res.reshape(vals_res.shape[:3])
                vals_obs = símismo.obs.obt_valor({**índs, 'días': eje_tiempo.días})

                dic = d_valid
                l_llaves = list(str(ll) for ll in índs.values())
                for ll in l_llaves[:-1]:
                    if ll not in dic:
                        dic[ll] = {}
                        dic = dic[ll]
                dic[l_llaves[-1]] = validar_matr_pred(vals_res, vals_obs)
            return d_valid

    def procesar_calib(símismo):
        if símismo._validable():
            l_proc = []
            pesos = []
            from spotpy.objectivefunctions import nashsutcliffe
            eje_tiempo = símismo.obs.eje_tiempo.cortar(símismo.tiempo.eje)
            for índs in símismo.obs.iter_índs(excluir='días'):
                matr_t = símismo.matr_t
                ejes_orig = np.argsort([matr_t.í_eje('días'), matr_t.í_eje('estoc'), matr_t.í_eje('parám')])

                vals_res = símismo.obt_valor_t(eje_tiempo, índs=índs)
                vals_res = np.moveaxis(vals_res, ejes_orig, [0, 1, 2])
                vals_res = vals_res.reshape(vals_res.shape[:3])
                vals_obs = símismo.obs.obt_valor({**índs, 'días': eje_tiempo.días})

                # l_proc.append(dens_con_pred(vals_obs, vals_res))
                l_proc.append(nashsutcliffe(vals_obs, np.mean(vals_res, axis=(1, 2))))
                pesos.append(np.sum(np.isfinite(vals_obs)))
            return np.average(l_proc, weights=pesos), np.sum(pesos)
        return 0, 0

    def obt_valor_t(símismo, t, índs=None):
        if símismo.matr_t is None:
            raise ValueError('Resultados no temporales no pueden dar datos temporales.')
        return símismo.matr_t.obt_val_t(t, índs=índs)

    def graficar(símismo, directorio=''):
        if símismo.matr_t:
            matr_t = símismo.matr_t
            for índs in matr_t.iter_índs(excluir=['días', 'estoc', 'parám']):
                ord_ejes = np.argsort([matr_t.í_eje('días'), matr_t.í_eje('estoc'), matr_t.í_eje('parám')])

                vals_res = símismo.obt_valor_t(símismo.tiempo.eje.vec(), índs=índs)
                vals_res = np.moveaxis(vals_res, ord_ejes, [0, 1, 2])
                try:
                    eje_obs = símismo.obs.eje_tiempo.cortar(símismo.tiempo.eje).vec()
                    vals_obs = símismo.obs.obt_valor({**índs, 'días': eje_obs})
                except (ValueError, AttributeError):  # para hacer: más elegante
                    vals_obs = eje_obs = None

                título = ', '.join(ll + ' ' + str(v) for ll, v in índs.items())

                graficar_pred(
                    título, directorio,
                    vals_res, t_pred=símismo.tiempo.eje.vec(), t_obs=eje_obs, vector_obs=vals_obs,
                )

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        matr = símismo.matr_t or símismo
        return reps_necesarias(
            matr.obt_valor(), eje_parám=matr.í_eje('parám'), eje_estoc=matr.í_eje('estoc'),
            frac_incert=frac_incert, confianza=confianza
        )

    def finalizar(símismo):
        pass

    def _validable(símismo):
        return símismo.matr_t is not None and símismo.obs is not None

    def __str__(símismo):
        return símismo.nombre


class ResultadosSimul(object):
    def __init__(símismo, módulos, tiempo):
        símismo.resultados = {mód: mód.resultados for mód in módulos if mód.resultados}
        símismo.tiempo = tiempo

    def reinic(símismo):
        for r in símismo:
            r.reinic()

    def actualizar_res(símismo):
        for r in símismo:
            r.actualizar()

    def finalizar(símismo):
        for r in símismo:
            r.finalizar()

    def procesar_calib(símismo):
        vals, pesos = zip(*[r.procesar_calib() for r in símismo])
        return np.average(vals, weights=pesos)

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        return {str(nmbr): mód.reps_necesarias(frac_incert, confianza) for nmbr, mód in símismo.resultados.items()}

    def validar(símismo):
        valid = {str(mód): res.validar() for mód, res in símismo.resultados.items()}
        return {ll: v for ll, v in valid.items() if v}

    def graficar(símismo, directorio=''):
        for mód, res in símismo.resultados.items():
            res.graficar(directorio=os.path.join(directorio, str(mód)))

    def __getitem__(símismo, itema):
        return símismo.resultados[next(mód for mód in símismo.resultados if str(mód) == str(itema))]

    def __iter__(símismo):
        for r in símismo.resultados.values():
            yield r


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

    def procesar_calib(símismo):
        vals, pesos = zip(*[r.procesar_calib() for r in símismo])
        return np.average(vals, weights=pesos), np.sum(pesos)

    def graficar(símismo, directorio):
        for nmb, res in símismo._resultados.items():
            res.graficar(directorio=os.path.join(directorio, nmb))

    def __getitem__(símismo, itema):
        return símismo._resultados[str(itema)]

    def __iter__(símismo):
        for r in símismo._resultados.values():
            yield r
