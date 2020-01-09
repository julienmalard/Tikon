import math as mat

import numpy as np
from scipy.stats import expon
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from ._plntll import EcuaciónDescomp
from ...utils import RES_CONC


class T50(Parám):
    nombre = 't50'
    líms = (0, None)
    unids = 'días'
    apriori = APrioriDist(expon(scale=100))


class DecaiExp(EcuaciónDescomp):
    nombre = 'Decaimiento Exponencial'
    cls_ramas = [T50]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        conc = símismo.obt_valor_mód(sim, RES_CONC)
        λ = mat.log(2) / cf['t50']
        return conc * (1 - (-λ * paso).fi(np.exp))
