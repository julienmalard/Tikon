import numpy as np

from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from .asimp_hum import AsimptóticoHumedad
from .constante import Constante
from .lognorm_temp import LogNormTemp
from .sig_temp import SigmoidalTemperatura


class EcMuerte(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [Constante, EcuaciónVacía, LogNormTemp, AsimptóticoHumedad, SigmoidalTemperatura]
    _nombre_res = MRTE
    _eje_cosos = EJE_ETAPA

    def postproc(símismo, paso):
        muertes = símismo.obt_res(filtrar=False)
        símismo.poner_val_res(np.round(muertes))


class EcsMuerte(CategEc):
    nombre = 'Muertes'
    cls_ramas = [EcMuerte]
    _nombre_res = MRTE
    _eje_cosos = EJE_ETAPA

    def postproc(símismo, paso):
        muertes = símismo.obt_res(filtrar=False)
        símismo.sim.quitar_pobs(muertes, etapas=símismo.cosos)
