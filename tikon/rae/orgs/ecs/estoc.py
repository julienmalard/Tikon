import numpy as np

from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía, Parám
from ._plntll_ec import EcuaciónOrg


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, 1)


class Normal(EcuaciónOrg):
    """
    Error distribuido de manera normal.
    """
    nombre = 'Normal'
    cls_ramas = [Sigma]

    def eval(símismo, paso):
        return símismo.cf['sigma'] * paso


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
        np.maximum(1, estoc, out=estoc)  # para hacer: bajar el ``1``...¿o no?
        estoc = np.random.normal(0, estoc)

        # Verificar que no quitamos más que existen
        estoc = np.where(-estoc > pobs, -pobs, estoc)

        símismo.mód.ajustar_pobs(estoc)
