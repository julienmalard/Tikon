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
        pobs_presas = símismo.pobs_etps(filtrar=False)
        pobs = símismo.pobs_etps()

        eje_etapa = símismo.í_eje(POBS, ETAPA)
        k = np.nansum(
            np.multiply(pobs_presas[tuple([slice(None)] * eje_etapa + [np.newaxis])], símismo.cf['K'])
            , axis=-1
        )  # Calcular la capacidad de carga

        return np.multiply(crec_etps, pobs * (1 - pobs / k))  # Ecuación logística sencilla
