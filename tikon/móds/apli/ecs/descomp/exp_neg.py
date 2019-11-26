import math as mat

import numpy as np
from tikon.ecs.árb_mód import Ecuación, Parám


class T50(Parám):
    nombre = 't50'
    líms = (0, None)
    unids = 'días'


class DecaiExp(Ecuación):
    nombre = 'Decaimiento Exponencial'
    cls_ramas = [T50]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        conc = símismo.obt_valor_res(sim)
        λ = mat.log(2) / cf['t50']
        return conc * (1 - np.exp(-λ * paso))
