class Calibrador(object):

    def __init__(símismo, func, paráms, calibs):
        símismo.func = func
        símismo.dists = calibs.gen_dists_calibs(paráms, permitidas=símismo.dists_disp)

    @property
    def dists_disp(símismo):
        raise NotImplementedError

    def calibrar(símismo, n_iter, nombre):
        raise NotImplementedError
