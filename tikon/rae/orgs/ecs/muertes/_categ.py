import numpy as np

from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from .asimp_hum import AsimptóticoHumedad
from .constante import Constante
from .lognorm_temp import LogNormTemp
from .sig_temp import SigmoidalTemperatura


class EcMuerte(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [EcuaciónVacía, Constante, LogNormTemp, AsimptóticoHumedad, SigmoidalTemperatura]
    auto = Constante
    _nombre_res = 'Muertes'
    _eje_cosos = 'etapa'

    def postproc(símismo, paso):
        muertes = símismo.obt_res(filtrar=False)
        símismo.poner_val_res(np.round(muertes))


class EcsMuerte(CategEc):
    nombre = 'Muertes'
    cls_ramas = [EcMuerte]
    _nombre_res = 'Muertes'
    _eje_cosos = 'etapa'

    def postproc(símismo, paso):
        muertes = símismo.obt_res(filtrar=False)
        símismo.mód.quitar_pobs(muertes, etapas=símismo.cosos)
