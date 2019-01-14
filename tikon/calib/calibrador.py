class Calibrador(object):

    def __init__(símismo, método, func, paráms, dists):
        símismo.método = método
        símismo.paráms = paráms
        símismo.func = func
        símismo.dists = dists

    def calibrar(símismo, n_iter):
        símismo._calibrar(n_iter)

    def _calibrar(símismo, n_iter):
        raise NotImplementedError

    @classmethod
    def métodos(cls):
        raise NotImplementedError
