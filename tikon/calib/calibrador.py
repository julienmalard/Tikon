class Calibrador(object):
    dists_disp = []

    def __init__(símismo, método, func, paráms, calibs):
        símismo.método = método
        símismo.func = func
        símismo.calibs = calibs
        símismo.dists = calibs.gen_dists_calibs(paráms, permitidas=símismo.dists_disp)

    def calibrar(símismo, n_iter, nombre):
        símismo._calibrar(n_iter, nombre=nombre)

    def _calibrar(símismo, n_iter, nombre):
        raise NotImplementedError

    @classmethod
    def métodos(cls):
        raise NotImplementedError
