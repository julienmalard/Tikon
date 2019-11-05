import numpy as np
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, 1)
    unids = None


class Normal(EcuaciónOrg):
    """
    Error distribuido de manera normal.
    """
    nombre = 'Normal'
    cls_ramas = [Sigma]

    def eval(símismo, paso, sim):
        pobs = símismo.pobs(sim)

        estoc = np.maximum(1, pobs * símismo.cf['sigma'] * paso)
        estoc[:] = np.random.normal(0, estoc)

        return estoc.round()
