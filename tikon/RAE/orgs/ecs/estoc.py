import numpy as np

from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import CategEc, SubcategEc, Ecuación, EcuaciónVacía


class PrSigma(Parám):
    nombre = 'sigma'
    líms = (0, 1)


class Normal(Ecuación):
    """
    Error distribuido de manera normal.
    """
    nombre = 'Normal'

    def __call__(símismo, paso):
        return símismo.cf['sigma'] * paso


class DistEstoc(SubcategEc):
    nombre = 'Dist'
    _cls_ramas = [EcuaciónVacía, Normal]
    auto = Normal


class EcsEstoc(CategEc):
    nombre = 'Estoc'
    _cls_ramas = [DistEstoc]

    def __call__(símismo, paso):
        super()(paso)

        estoc = símismo._res.obt_valor()
        np.multiply(pobs, estoc, out=estoc)
        np.maximum(1, estoc, out=estoc)
        np.round(np.random.normal(0, estoc), out=estoc)

        # Verificar que no quitamos más que existen
        estoc[:] = np.where(-estoc > pobs, -pobs, estoc)
