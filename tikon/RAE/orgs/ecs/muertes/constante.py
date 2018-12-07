import numpy as np

from tikon.ecs.árb_mód import Ecuación, Parám


class Q(Parám):
    nombre = 'q'
    líms = (0, 1)


class Constante(Ecuación):
    """
    Muertes en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición exponencial.
    """
    nombre = 'Constante'
    _cls_ramas = [Q]

    def __call__(self, paso):
        return np.multiply(pob_etp, cf['q'])
