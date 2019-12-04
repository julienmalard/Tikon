from scipy.stats import expon
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.utils import RES_DEPR, EJE_VÍCTIMA

from ._plntll_ec import EcuaciónRepr


class N(Parám):
    nombre = 'n'
    líms = (0, None)
    unids = None
    inter = ['presa']
    apriori = APrioriDist(expon(scale=10))


class Depred(EcuaciónRepr):
    """
    Reproducciones en función de la depredación (útil para avispas esfécidas)
    """
    nombre = 'Depredación'
    cls_ramas = [N]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        depred = símismo.obt_valor_mód(sim, RES_DEPR, filtrar=False)

        pobs = símismo.pobs(sim)  # Paso ya se tomó en cuenta con depredaciones
        return (cf['n'] * depred).sum(dim=EJE_VÍCTIMA) * pobs
