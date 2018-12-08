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
    cls_ramas = [Q]

    def eval(self, paso):
        return np.multiply(pob_etp, cf['q'])
