import numpy as np

from ..orgs.ecs import ecs_etps_orgs


class MnjdrEcsRed(object):
    def __init__(símismo, etapas, calibs, n_rep_paráms):
        símismo._etapas = etapas
        d_categs = {
            'Edad': CategEdad,
            'Depredación': CategDepred,
            'Crecimiento': CategCrec,
            'Reproducción': CategReprod,
            'Muertes': CategMuertes,
            'Transiciones': CategTransiciones,
            'Movimiento': CategMovimiento,
            'Estoc': CategEstoc
        }
        símismo._categs = {
            ctg: cls_ctg(ctg, ecs_etps_orgs, etapas=_etps_activas(etapas, ctg)) for ctg, cls_ctg in d_categs.items()
        }
        símismo._gen_coefs(calibs, n_rep_paráms)
        símismo.paráms =

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
