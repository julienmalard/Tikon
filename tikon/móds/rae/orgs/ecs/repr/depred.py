from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg
from tikon.móds.rae.red.utils import RES_DEPR, EJE_VÍCTIMA


class N(Parám):
    nombre = 'n'
    líms = (0, 1)
    unids = None


class Depred(EcuaciónOrg):
    """
    Reproducciones en función de la depredación (útil para avispas esfécidas)
    """
    nombre = 'Depred'
    cls_ramas = [N]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        depred = símismo.obt_val_mód(sim, RES_DEPR)
        pobs = símismo.pobs(sim)  # Paso ya se tomó en cuenta con depredaciones
        return (cf['n'] * depred).sum(dim=EJE_VÍCTIMA) * pobs
