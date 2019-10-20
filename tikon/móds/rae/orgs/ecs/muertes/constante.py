import numpy as np

from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónMuertes


class Q(Parám):
    nombre = 'q'
    líms = (0, 1)


class Constante(EcuaciónMuertes):
    """
    Muertes en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición exponencial.
    """
    nombre = 'Constante'
    cls_ramas = [Q]

    def eval(símismo, paso):
        pobs = símismo.obt_val_mód(POBS)
        return np.multiply(pobs, símismo.cf['q'])
