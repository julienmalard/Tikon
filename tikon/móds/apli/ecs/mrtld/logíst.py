import numpy as np
from scipy.stats import expon, uniform
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from ._plntll import EcuaciónMortalidad
from ...utils import RES_CONC


class L50(Parám):
    """Dósis de letalidad 50% en un día"""
    nombre = 'l50'
    líms = (0, None)
    unids = 'kg / ha'
    inter = 'etapa'
    apriori = APrioriDist(expon(scale=5))


class B(Parám):
    nombre = 'b'
    líms = (0, None)
    unids = None
    inter = 'etapa'
    apriori = APrioriDist(uniform(0, 100))


class Logística(EcuaciónMortalidad):
    nombre = 'Mortalidad logística'
    cls_ramas = [L50, B]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        conc = símismo.obt_valor_mód(sim, RES_CONC, filtrar=False)

        return 1 / (1 + (-cf['b'] * (conc - cf['l50'])).fi(np.exp))
