from SALib.analyze import delta, dgsm, fast, ff as ff_anlz, morris as morris_anlz, sobol
from SALib.sample import fast_sampler, ff as ff_muestra, latin, morris as morris_muestra, saltelli

from .sensib import AnlzdrSensib


class SensSALib(AnlzdrSensib):
    métodos = ['sobol', 'fast', 'morris', 'dmim', 'dgsm', 'ff']

    def __init__(símismo, método, paráms, calibs):
        super().__init__(método, paráms, calibs)

        n_prms = len(símismo.dists)
        símismo.problema = {
            'num_vars': n_prms,  # El número de parámetros
            'names': [str(i) for i in range(n_prms)],  # Nombres numéricos muy sencillos
            'bounds': [d.aprox_líms(0.95) for d in símismo.dists]  # Lista de límites aproximativos
        }

    def _gen_muestrea(símismo, n, ops):
        if símismo.método == 'sobol':
            return saltelli.sample(problem=símismo.problema, N=n, **ops)
        elif símismo.método == 'fast':
            return fast_sampler.sample(problem=símismo.problema, N=n, **ops)
        elif símismo.método == 'morris':
            return morris_muestra.sample(problem=símismo.problema, N=n, **ops)
        elif símismo.método == 'dmim':
            return latin.sample(problem=símismo.problema, N=n)
        elif símismo.método == 'dgsm':
            return saltelli.sample(problem=símismo.problema, N=n)
        elif símismo.método == 'ff':
            return ff_muestra.sample(problem=símismo.problema)
        else:
            raise ValueError('Método de análisis de sensibilidad "{}" no reconocido.'.format(símismo.método))

    def _analizar(símismo, vec_res, muestra, ops):

        if símismo.método == 'sobol':
            return sobol.analyze(problem=símismo.problema, Y=vec_res, **ops)
        elif símismo.método == 'fast':
            return fast.analyze(problem=símismo.problema, Y=vec_res, **ops)
        elif símismo.método == 'morris':
            return morris_anlz.analyze(problem=símismo.problema, X=muestra, Y=vec_res, **ops)
        elif símismo.método == 'dmim':
            return delta.analyze(problem=símismo.problema, X=muestra, Y=vec_res, **ops)
        elif símismo.método == 'dgsm':
            return dgsm.analyze(problem=símismo.problema, X=muestra, Y=vec_res, **ops)
        elif símismo.método == 'ff':
            return ff_anlz.analyze(problem=símismo.problema, X=muestra, Y=vec_res, **ops)
        else:
            raise ValueError('Método de análisis de sensibilidad "{}" no reconocido.'.format(símismo.método))
