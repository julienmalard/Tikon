from SALib.analyze import delta, dgsm, fast, ff as ff_anlz, morris as morris_anlz, sobol
from SALib.sample import fast_sampler, ff as ff_muestra, latin, morris as morris_muestra, saltelli

from .sensib import AnlzdrSensib, MuestraSensib


class SensSALib(AnlzdrSensib):
    def __init__(símismo, n=4, método='sobol', prc=0.95, ops_muestreo=None, ops_anlzr=None):
        símismo.prc = prc
        símismo.n = n
        símismo.método = método.lower()
        símismo.ops_muestreo = ops_muestreo or {}
        símismo.ops_anlzr = ops_anlzr or {}
        super().__init__()

    def _problema(símismo, dists):
        n_prms = len(dists)
        return {
            'num_vars': n_prms,  # El número de parámetros
            'names': [str(i) for i in range(n_prms)],  # Nombres numéricos muy sencillos
            'bounds': [d.aprox_líms(símismo.prc) for d in dists]  # Lista de límites aproximativos
        }

    def filtrar_paráms(símismo, paráms):
        return [d for d in paráms if d.aprox_líms(símismo.prc)[0] != d.aprox_líms(símismo.prc)[1]]

    def muestrear(símismo, dists):
        n = len(dists)
        problema = símismo._problema(dists)
        ops = símismo.ops_muestreo

        if símismo.método == 'sobol':
            mstr = saltelli.sample(problem=problema, N=n, **ops)
        elif símismo.método == 'fast':
            mstr = fast_sampler.sample(problem=problema, N=n, **ops)
        elif símismo.método == 'morris':
            mstr = morris_muestra.sample(problem=problema, N=n, **ops)
        elif símismo.método == 'dmim':
            mstr = latin.sample(problem=problema, N=n)
        elif símismo.método == 'dgsm':
            mstr = saltelli.sample(problem=problema, N=n)
        elif símismo.método == 'ff':
            mstr = ff_muestra.sample(problem=problema)
        else:
            raise ValueError('Método de análisis de sensibilidad "{}" no reconocido.'.format(símismo.método))
        return MuestraSensib(mstr.shape[1], mstr)

    def _analizar(símismo, vec_res, muestra, dists):
        problema = símismo._problema(dists)
        ops = símismo.ops_anlzr
        if símismo.método == 'sobol':
            return sobol.analyze(problem=problema, Y=vec_res, **ops)
        elif símismo.método == 'fast':
            return fast.analyze(problem=problema, Y=vec_res, **ops)
        elif símismo.método == 'morris':
            return morris_anlz.analyze(problem=problema, X=muestra, Y=vec_res, **ops)
        elif símismo.método == 'dmim':
            return delta.analyze(problem=problema, X=muestra, Y=vec_res, **ops)
        elif símismo.método == 'dgsm':
            return dgsm.analyze(problem=problema, X=muestra, Y=vec_res, **ops)
        elif símismo.método == 'ff':
            return ff_anlz.analyze(problem=problema, X=muestra, Y=vec_res, **ops)
        else:
            raise ValueError('Método de análisis de sensibilidad "{}" no reconocido.'.format(símismo.método))
