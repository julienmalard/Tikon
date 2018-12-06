from tikon.ecs.paráms import Parám
from ._plntll_ec import EcuaciónCrec
import numpy as np

class K(Parám):
    nombre = 'K'
    líms = (0, None)
    inter = 'presa'


class LogístDepred(EcuaciónCrec):
    """
    Crecimiento proporcional a la cantidad de presas que se consumió el depredador.
    """
    nombre = 'Logístico Depredación'
    _cls_ramas = [K]

    def __call__(símismo, paso):
        #
        crec_etps = símismo.crec_etps()
        pobs_etps = símismo.pobs_etps()

        res_depred = símismo.í_eje(eje='presa', res='Depred')
        depred = símismo.obt_val_mód('Depred', índs={'etapa': símismo._í_cosos})  # La depredación por estas etapas
        eje_presa = res_depred.í_eje('presa')

        k = np.nansum(np.multiply(depred, símismo.cf['K']), axis=eje_presa)  # Calcular la capacidad de carga
        crec_etps = np.multiply(crec_etps, pobs_etps * (1 - pobs_etps / k))  # Ecuación logística sencilla

        # Evitar péridadas de poblaciones superiores a la población.
        return np.maximum(crec_etps, -pobs_etps)
