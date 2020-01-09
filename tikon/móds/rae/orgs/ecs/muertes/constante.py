from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónMuertes


class Q(Parám):
    nombre = 'q'
    líms = (0, 1)
    unids = None


class Constante(EcuaciónMuertes):
    """
    Muertes en proporción al tamaño de la población. Sin crecimiento, esto da un decaimiento exponencial.

    """

    nombre = 'Constante'
    cls_ramas = [Q]

    def eval(símismo, paso, sim):
        return símismo.cf['q']
