class Calibrador(object):

    def __init__(símismo, método, func, l_paráms):
        símismo.método = método
        símismo.paráms = l_paráms
        símismo.func = func

    def calibrar(símismo, n_iter):
        for pr in símismo.paráms:
            pr.estab_calib_activa(n_iter)

        símismo._calibrar(n_iter)

    def _calibrar(símismo, n_iter):
        raise NotImplementedError

    @classmethod
    def métodos(cls):
        raise NotImplementedError
