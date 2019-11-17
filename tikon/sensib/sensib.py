import os

import numpy as np


class AnlzdrSensib(object):
    dists_disp = None

    def __init__(símismo, paráms, calibs):
        símismo.calibs = calibs
        dists = calibs.gen_dists_calibs(paráms, permitidas=símismo.dists_disp)
        # ...y para hacer: más elegante, por supuesto:
        símismo.dists = {d: vls for d, vls in dists.items() if d.aprox_líms(0.95)[0] != d.aprox_líms(0.95)[1]}
        símismo.mstr = None

    def aplicar_muestrea(símismo, n, ops):
        símismo.mstr = símismo._gen_muestrea(n, ops)
        for v, v_prm in zip(símismo.mstr, símismo.dists.values()):
            for vl in v_prm:
                vl.poner_val(v)

    def analizar(símismo, resultados, ops):
        f = lambda x: símismo._analizar(x, símismo.mstr, ops=ops)
        return ResSensibCorrida(resultados, f)

    def _gen_muestrea(símismo, n, ops):
        raise NotImplementedError

    def _analizar(símismo, vec_res, muestra, ops):
        raise NotImplementedError


# para hacer: ¿combinar con Resultados normales?
class ResSensibCorrida(object):
    def __init__(símismo, res, func):
        símismo.func = func
        símismo._resultados = {str(r): ResSensibMódulo(r, func) for r in res}

    def dibujar(símismo, directorio=''):
        for nmb, res in símismo._resultados.items():
            res.graficar(directorio=os.path.join(directorio, nmb))

    def __iter__(símismo):
        for r in símismo._resultados.values():
            yield r

    def __getitem__(símismo, itema):
        return símismo._resultados[itema]


class ResSensibMódulo(object):
    def __init__(símismo, res, func):
        símismo.func = func
        símismo._resultados = {str(r): ResSensibResultado(r, func) for r in res}

    def dibujar(símismo, directorio=''):
        for nmb, res in símismo._resultados.items():
            res.graficar(directorio=os.path.join(directorio, nmb))

    def __iter__(símismo):
        for r in símismo._resultados.values():
            yield r

    def __getitem__(símismo, itema):
        return símismo._resultados[itema]


class ResSensibResultado(object):
    def __init__(símismo, res, func):
        símismo.func = func
        símismo.res = res
        símismo.sensib = símismo._calc_sensib()

    def _calc_sensib(símismo):

        # El diccionario para los resultados
        d_sens = {}

        matr_t = símismo.res.matr_t
        for índs in matr_t.iter_índs(excluir=[EJE_TIEMPO, EJE_ESTOC, EJE_PARÁM]):
            ejes_orig = np.argsort([matr_t.í_eje(EJE_TIEMPO), matr_t.í_eje(EJE_ESTOC), matr_t.í_eje(EJE_PARÁM)])

            vals_res = matr_t.obt_valor_t(índs=índs)
            vals_res = np.moveaxis(vals_res, ejes_orig, [0, 1, 2])
            vals_res = vals_res.reshape(vals_res.shape[:3]).mean(axis=(1, 2))

            l_llaves = list(str(ll) for ll in índs.values())
            for ll in l_llaves[:-1]:
                if ll not in d_sens:
                    d_sens[ll] = {}
                    d_sens = d_sens[ll]

            d_sensib_índ = {}
            for í, vals_t in enumerate(vals_res):
                sensib = símismo.func(vals_t)
                for egr, m_egr in sensib.items():
                    # Para cada tipo de egreso del análisis de sensibilidad...

                    # Crear la matriz de resultados vacía, si necesario
                    if egr not in d_sensib_índ:
                        d_sensib_índ[egr] = np.zeros((*m_egr.shape, len(vals_res)))

                    # Llenar los datos para este día
                    d_sensib_índ[egr][..., í] = sensib[egr]

            d_sens[l_llaves[-1]] = d_sensib_índ

        return d_sens

    def dibujar(símismo, directorio=''):
        matr_t = símismo.res.matr_t
        for índs in matr_t.iter_índs(excluir=[EJE_TIEMPO, EJE_ESTOC, EJE_PARÁM]):
            l_llaves = list(str(ll) for ll in índs.values())
            d_sensib = símismo.sensib
            for ll in l_llaves:
                d_sensib = d_sensib[ll]

            medidas = list(d_sensib)

            graficar_línea()
