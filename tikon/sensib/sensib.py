class AnlzdrSensib(object):
    dists_disp = None

    def aplicar_muestreo(símismo, muestreo, sim):
        paráms = símismo.filtrar_paráms(sim.paráms)
        for v, v_prm in zip(muestreo, paráms):
            for vl in v_prm:
                vl.poner_val(v)

    def analizar(símismo, sim, muestreo, proc):
        f = lambda x: símismo._analizar(x, muestreo, sim.paráms)
        return ResSensibCorrida(resultados, f)

    def filtrar_paráms(símismo, paráms):
        dists = calibs.gen_dists_calibs(paráms, permitidas=símismo.dists_disp)

    def muestrear(símismo, paráms):
        raise NotImplementedError

    def _analizar(símismo, vec_res, muestra, dists):
        raise NotImplementedError


class MuestraSensib(object):
    def __init__(símismo, tmñ, muestras):
        símismo.tmñ = tmñ
        símismo.muestras = muestras

    def __iter__(símismo):
        for m in símismo.muestras:
            yield m
