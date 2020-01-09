from scipy.stats import expon
from tikon.ecs import Parám
from tikon.ecs.aprioris import APrioriDist

from .._plntll import EcuaciónMov


class D(Parám):
    nombre = 'd'
    líms = (0, None)
    unids = 'm2 / día'
    apriori = APrioriDist(expon(scale=1000))


class Euclidiana(EcuaciónMov):
    nombre = 'Euclidiana'
    cls_ramas = [D]

    def eval(símismo, paso, sim):
        # Devolvemos distancia cuadrada
        return símismo.obt_valor_control(sim, 'distancias') ** 2 / (símismo.cf['d'] * paso)

    @classmethod
    def requísitos(cls, controles=False):
        if controles:
            return {'distancias'}
