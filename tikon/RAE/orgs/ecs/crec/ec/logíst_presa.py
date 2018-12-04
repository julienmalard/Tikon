import numpy as np

from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class K(Parám):
    nombre = 'K'
    líms = (0, None)
    inter = 'presa'


class LogístPresa(Ecuación):
    """
    Crecimiento logístico. 'K' es un parámetro repetido para cada presa de la etapa y indica
    la contribución individual de cada presa a la capacidad de carga de esta etapa (el depredador).
    """

    nombre = 'Logístico Presa'
    _cls_ramas = [K]

    def __call__(símismo, paso):
        k = np.nansum(np.multiply(pobs[..., np.newaxis, :], cf['K']), axis=-1)  # Calcular la capacidad de carga
        np.multiply(crec_etp, pobs_etps * (1 - pobs_etps / k), out=crec_etp)  # Ecuación logística sencilla

        # Evitar pérdidas de poblaciones superiores a la población.
        return np.maximum(crec_etp, -pobs_etps)
