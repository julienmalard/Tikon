import numpy as np

from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónTrans


class Q(Parám):
    nombre = 'q'
    líms = (0, 1)


class Constante(EcuaciónTrans):
    """
    Transiciones en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
    exponencial.
    """

    def eval(símismo, paso):
        cf = símismo.cf
        pobs = símismo.obt_val_mód(POBS)

        # Tomamos el paso en cuenta según las reglas de probabilidades conjuntas:
        # p(x sucede n veces) = (1 - (1- p(x))^n)
        return np.multiply(pobs, (1 - (1 - cf['q']) ** paso))

    nombre = 'Constante'
    cls_ramas = [Q]
