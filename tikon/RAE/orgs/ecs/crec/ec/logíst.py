import numpy as np

from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class K(Parám):
    nombre = 'K'
    líms = (0, None)


class Logíst(Ecuación):
    """
    Ecuación logística sencilla
    """

    nombre = 'Logístico'
    _cls_ramas = [K]

    def __call__(símismo, paso):
        return np.multiply(crec_etp, pobs_etps * (1 - pobs_etps / símismo.cf['K']))
