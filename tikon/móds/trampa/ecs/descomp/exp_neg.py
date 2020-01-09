import math as mat

import numpy as np
from scipy.stats import expon
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from ._plntll import EcuaciónDescomp
from ...utils import RES_DENS


class T50(Parám):
    nombre = 't50'
    líms = (0, None)
    unids = 'días'
    apriori = APrioriDist(expon(scale=300))


class DecaiExp(EcuaciónDescomp):
    nombre = 'Decaimiento Exponencial'
    cls_ramas = [T50]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        dens = símismo.obt_valor_mód(sim, RES_DENS)
        λ = mat.log(2) / cf['t50']
        return dens * (1 - (-λ * paso).fi(np.exp))
