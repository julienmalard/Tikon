import numpy as np


class Resultado(object):
    def __init__(símismo, dims, í_pasos, obs=None):
        símismo.matr = np.zeros(dims.frm())
        símismo.í_pasos = í_pasos
        símismo.obs = obs

    def rebanar(símismo, dim, índs):
        rbnd =
        return símismo.matr[rbnd]

    def matr_obs(símismo):
        pass



    def validar(símismo):
        pass

    def graficar(símismo):
        pass


class Obs(object):
    def __init__(símismo, datos, í_pasos):
        símismo.datos = datos
        símismo.í_pasos = í_pasos


class Dims(object):
    def __init__(símismo, n_estoc, n_parám, n_parc, dims=None):
        if dims is None:
            dims = {}
        símismo._frm = (n_parc, n_estoc, n_parám, *dims.values())
        símismo.dims = dims

    def

    def frm(símismo):
        return símismo._frm
