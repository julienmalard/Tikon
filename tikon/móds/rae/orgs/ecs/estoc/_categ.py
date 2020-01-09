import numpy as np

from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import CategEcOrg, SubcategEcOrg
from tikon.móds.rae.orgs.ecs.utils import ECS_ESTOC
from tikon.móds.rae.utils import RES_ESTOC
from .normal import Normal


class DistEstoc(SubcategEcOrg):
    nombre = 'Dist'
    cls_ramas = [Normal, EcuaciónVacía]
    _nombre_res = RES_ESTOC


class EcsEstoc(CategEcOrg):
    nombre = ECS_ESTOC
    cls_ramas = [DistEstoc]
    _nombre_res = RES_ESTOC

    def postproc(símismo, paso, sim):
        estoc = símismo.obt_valor_res(sim).f(np.round)
        pobs = símismo.pobs(sim)

        # Verificar que no quitemos más que existen
        estoc = estoc.donde(-estoc < pobs, -pobs)

        símismo.poner_valor_res(sim, estoc)
        símismo.ajust_pobs(sim, estoc)
