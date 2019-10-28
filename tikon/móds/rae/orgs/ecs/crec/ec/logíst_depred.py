import xarray as xr
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.red.utils import EJE_VÍCTIMA, RES_DEPR

from ._plntll_ec import EcuaciónCrec


class K(Parám):
    nombre = 'K'
    líms = (0, None)
    inter = 'presa'
    unids = 'individual'


class LogístDepred(EcuaciónCrec):
    """
    Crecimiento proporcional a la cantidad de presas que se consumió el depredador.
    """
    nombre = 'Logístico Depredación'
    cls_ramas = [K]

    def eval(símismo, paso, sim):
        crec_etps = símismo.obt_val_res(sim)
        pobs_etps = símismo.pobs(sim)

        depred = símismo.obt_val_mód(sim, var=RES_DEPR)  # La depredación por estas etapas

        k = (depred * símismo.cf['K']).sum(dim=EJE_VÍCTIMA)  # Calcular la capacidad de carga
        return crec_etps * (pobs_etps * (1 - pobs_etps / k))  # Ecuación logística sencilla
