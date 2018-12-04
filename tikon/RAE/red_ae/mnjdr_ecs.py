import numpy as np

from ..orgs.ecs import ecs_etps_orgs


class MnjdrEcsRed(object):
    def __init__(símismo, etapas, calibs, n_rep_paráms):
        símismo._etapas = etapas

        símismo._gen_coefs(calibs, n_rep_paráms)

    def etapas_categ(símismo, categ):
        return símismo[categ].etapas

    def _gen_coefs(símismo, calibs, n_rep_paráms):
        pass


    def __getitem__(símismo, itema):
        return símismo._categs[itema]


class EcSimul(object):
    def __init__(símismo, func, paráms, í_etapas):
        símismo.func = func
        símismo.paráms = paráms
        símismo.í_etapas = í_etapas

    def evaluar(símismo, paso, res):
        val = símismo.func(paráms=símismo.paráms, paso=paso, mód=mód)
        res.poner_val(val, símismo.í_etapas)



class MatrValoresParám(object):
    def __init__(símismo, dists):
        símismo.dists = dists
        símismo.vals = np.array(dists, dtype=float)

    def __float__(símismo):
        símismo.vals[:] = símismo.dists
        return símismo.vals
