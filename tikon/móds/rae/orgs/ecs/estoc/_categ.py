import numpy as np

from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from .normal import Normal


class DistEstoc(SubcategEc):
    nombre = 'Dist'
    cls_ramas = [EcuaciónVacía, Normal]
    auto = Normal
    _eje_cosos = 'etapa'
    _nombre_res = 'Estoc'


class EcsEstoc(CategEc):
    nombre = 'Estoc'
    cls_ramas = [DistEstoc]
    _nombre_res = 'Estoc'
    _eje_cosos = 'etapa'

    def postproc(símismo, paso):
        estoc = símismo.obt_res(filtrar=False)
        pobs = símismo.obt_val_mód('Pobs', filtrar=True)

        np.multiply(pobs, estoc, out=estoc)
        np.maximum(1, estoc, out=estoc)
        estoc = np.random.normal(0, estoc)
        estoc = np.round(estoc)

        # Verificar que no quitamos más que existen
        estoc = np.where(-estoc > pobs, -pobs, estoc)

        símismo.poner_val_res(estoc)
        símismo.mód.ajustar_pobs(estoc)
