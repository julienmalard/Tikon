from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg
from tikon.móds.rae.utils import RES_DEPR, EJE_VÍCTIMA


class N(Parám):
    nombre = 'n'
    líms = (0, 1)
    unids = None
    inter = ['presa']


class Depred(EcuaciónOrg):
    """
    Reproducciones en función de la depredación (útil para avispas esfécidas)
    """
    nombre = 'Depredación'
    cls_ramas = [N]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        depred = símismo.obt_valor_mód(sim, RES_DEPR)
        pobs = símismo.pobs(sim)  # Paso ya se tomó en cuenta con depredaciones
        return (cf['n'] * depred).sum(dim=EJE_VÍCTIMA) * pobs
