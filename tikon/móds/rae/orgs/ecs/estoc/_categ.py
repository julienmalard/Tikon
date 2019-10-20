import numpy as np

from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.rae.orgs.utils import ESTOC

from .normal import Normal


class DistEstoc(SubcategEc):
    nombre = 'Dist'
    cls_ramas = [EcuaciónVacía, Normal]
    auto = Normal
    _eje_cosos = ETAPA
    _nombre_res = ESTOC


class EcsEstoc(CategEc):
    nombre = ESTOC
    cls_ramas = [DistEstoc]
    _nombre_res = ESTOC
    _eje_cosos = ETAPA

    def postproc(símismo, paso):
        estoc = símismo.obt_res(filtrar=False)
        pobs = símismo.obt_val_mód(POBS, filtrar=True)

        np.multiply(pobs, estoc, out=estoc)
        np.maximum(1, estoc, out=estoc)
        estoc = np.random.normal(0, estoc)
        estoc = np.round(estoc)

        # Verificar que no quitamos más que existen
        estoc = np.where(-estoc > pobs, -pobs, estoc)

        símismo.poner_val_res(estoc)
        símismo.sim.ajustar_pobs(estoc)
