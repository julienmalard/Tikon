from tikon.ecs.árb_mód import Parám
from tikon.rae.orgs.ecs._plntll_ec import EcuaciónOrg


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
