from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class K(Parám):
    nombre = 'K'
    líms = (0, None)
    inter = 'presa'


class LogístDepred(Ecuación):
    """
    Crecimiento proporcional a la cantidad de presas que se consumió el depredador.
    """
    nombre = 'Logístico Depredación'
    _cls_ramas = [K]

    def __call__(símismo, paso):
        #

        depred = símismo.predics['Depred'][..., í_etps, :]  # La depredación por esta etapa
        k = np.nansum(np.multiply(depred, cf['K']), axis=3)  # Calcular la capacidad de carga
        np.multiply(crec_etp, pobs_etps * (1 - pobs_etps / k), out=crec_etp)  # Ecuación logística sencilla

        # Evitar péridadas de poblaciones superiores a la población.
        np.maximum(crec_etp, -pobs_etps, out=crec_etp)