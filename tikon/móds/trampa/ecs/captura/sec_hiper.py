from math import pi as π

from scipy.stats import expon
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from ._plntll import EcuaciónCaptura


class R(Parám):
    """El rayo al cual la probabilidad de captura = 2/(1/e+e) ≈ 64.8%."""
    nombre = 'r'
    líms = (0, None)
    unids = 'm'
    inter = 'etapa'
    apriori = APrioriDist(expon(scale=5))


class SecanteHiperbólica(EcuaciónCaptura):
    nombre = 'Secante hiperbólica'
    cls_ramas = [R]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        # El integral de la secante hiperbólica es π
        return (π * cf['r']) ** 2 / 10000
