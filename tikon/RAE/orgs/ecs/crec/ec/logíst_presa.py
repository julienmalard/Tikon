import numpy as np

from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónCrec


class K(Parám):
    nombre = 'K'
    líms = (0, None)
    inter = 'presa'


class LogístPresa(EcuaciónCrec):
    """
    Crecimiento logístico. 'K' es un parámetro repetido para cada presa de la etapa y indica
    la contribución individual de cada presa a la capacidad de carga de esta etapa (el depredador).
    """

    nombre = 'Logístico Presa'
    cls_ramas = [K]

    def eval(símismo, paso):
        crec_etps = símismo.crec_etps()
        pobs_etps = símismo.pobs_etps()

        k = np.nansum(np.multiply(pobs[..., np.newaxis, :], símismo.cf['K']), axis=-1)  # Calcular la capacidad de carga
        np.multiply(crec_etps, pobs_etps * (1 - pobs_etps / k), out=crec_etps)  # Ecuación logística sencilla

        # Evitar pérdidas de poblaciones superiores a la población.
        return np.maximum(crec_etps, -pobs_etps)
