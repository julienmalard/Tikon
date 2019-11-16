class Calibrador(object):

    @property
    def dists_disp(símismo):
        raise NotImplementedError

    def calibrar(símismo, nombre, func, calibs, paráms, n_iter):
        dists = calibs.gen_dists_calibs(paráms, permitidas=símismo.dists_disp)

        pesos, calibradas = símismo._calc_calib(func, dists, n_iter)

        for cnx, vals in zip(dists, calibradas):
            cnx.guardar_traza(nombre=nombre, vals=vals, pesos=pesos)

    def _calc_calib(símismo, func, dists, n_iter):
        raise NotImplementedError
