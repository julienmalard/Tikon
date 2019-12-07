import numpy as np
from scipy.stats import norm, expon
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónMuertes


class A(Parám):
    nombre = 'a'
    líms = (None, None)
    unids = 'C'
    apriori = APrioriDist(norm(20, 10))


class B(Parám):
    nombre = 'b'
    líms = (0, None)
    unids = 'C'
    apriori = APrioriDist(expon(scale=10))


class SigmoidalTemperatura(EcuaciónMuertes):
    """
    Sobrevivencia que disminuye con temperatura creciente según relación sigmoidal.
    """

    nombre = 'Sigmoidal Temperatura'
    cls_ramas = [A, B]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        temp_máx = símismo.obt_valor_extern(sim, 'clima.temp_máx')
        sobrevivencia = 1 / (1 + ((temp_máx - cf['a']) / cf['b']).fi(np.exp))
        return 1 - sobrevivencia

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_máx'}
