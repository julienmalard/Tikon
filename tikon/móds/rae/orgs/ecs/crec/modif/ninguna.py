from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg


class R(Parám):
    nombre = 'r'
    líms = (0, None)
    unids = None


class Ninguna(EcuaciónOrg):
    nombre = 'Ninguna'
    cls_ramas = [R]

    def eval(símismo, paso, sim):
        # Sin modificación a r.
        return símismo.cf['r'] * paso
