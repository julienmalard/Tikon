from tikon.ecs.aprioris import APrioriDens
from tikon.ecs.árb_mód import Parám
from ._plntll_ec import ModCrec


class R(Parám):
    nombre = 'r'
    líms = (0, None)
    unids = None
    apriori = APrioriDens((0, 0.1), 0.9)


class Ninguna(ModCrec):
    nombre = 'Ninguna'
    cls_ramas = [R]

    def eval(símismo, paso, sim):
        # Sin modificación a r.
        return símismo.cf['r'] * paso
