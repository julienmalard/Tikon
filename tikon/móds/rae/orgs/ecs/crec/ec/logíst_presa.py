import numpy as np
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.utils import EJE_VÍCTIMA

from ._plntll_ec import EcuaciónCrec


class K(Parám):
    nombre = 'K'
    líms = (0, None)
    inter = 'presa'
    unids = 'individual'


class LogístPresa(EcuaciónCrec):
    """
    Crecimiento logístico. 'K' es un parámetro repetido para cada presa de la etapa y indica
    la contribución individual de cada presa a la capacidad de carga de esta etapa (el depredador).
    """

    nombre = 'Logístico Presa'
    cls_ramas = [K]

    def eval(símismo, paso, sim):
        crec_etps = símismo.obt_valor_res(sim)
        pobs_presas = símismo.pobs(sim, filtrar=False)
        pobs = símismo.pobs(sim)

        k = np.maximum(1, (pobs_presas * símismo.cf['K']).suma(dim=EJE_VÍCTIMA))  # Calcular la capacidad de carga

        return crec_etps * pobs * (1 - pobs / k)  # Ecuación logística sencilla
