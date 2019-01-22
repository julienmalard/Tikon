import numpy as np

from tikon.ecs.árb_mód import Ecuación, Parám


class N(Parám):
    nombre = 'n'
    líms = (0, 1)


class Depred(Ecuación):
    """
    Reproducciones en función de la depredación (útil para avispas esfécidas)
    """
    nombre = 'Depred'
    cls_ramas = [N]

    def eval(símismo, paso):
        cf = símismo.cf
        return np.sum(np.multiply(cf['n'], depred[..., í_etps, :]), axis=-1)
