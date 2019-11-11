class Calibrador(object):

    def __init__(símismo, **args):
        símismo.args = args

    @property
    def dists_disp(símismo):
        raise NotImplementedError

    def calibrar(símismo, nombre, func, calibs, paráms, n_iter):
        dists = calibs.gen_dists_calibs(paráms, permitidas=símismo.dists_disp)

        calibradas = símismo._calc_calib(func, dists)

        for cnx, (vals, pesos) in zip(dists, calibradas):
            cnx.guardar_traza(nombre=nombre, vals=vals, pesos=pesos)

    def _calc_calib(símismo, func, dists):
        raise NotImplementedError
