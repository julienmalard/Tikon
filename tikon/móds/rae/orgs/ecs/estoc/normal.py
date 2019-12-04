import numpy as np
from tikon.ecs.aprioris import APrioriDens
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs.estoc._plntll_ec import EcuaciónEstoc


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, 1)
    unids = None
    apriori = APrioriDens((0, 0.05), 0.95)


class Normal(EcuaciónEstoc):
    """
    Error distribuido de manera normal.
    """
    nombre = 'Normal'
    cls_ramas = [Sigma]

    def eval(símismo, paso, sim):
        pobs = símismo.pobs(sim)

        estoc = np.maximum(1, pobs * símismo.cf['sigma'] * paso)
        estoc.values[:] = np.random.normal(0, estoc.values)  # [:] necesario para mantener formato xr.DataArray

        return estoc
