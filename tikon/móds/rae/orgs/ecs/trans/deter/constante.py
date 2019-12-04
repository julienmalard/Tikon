from tikon.ecs.árb_mód import Parám

from .._plntll_ec import EcuaciónTrans


class Q(Parám):
    nombre = 'q'
    líms = (0, 1)
    unids = None


class Constante(EcuaciónTrans):
    """
    Transiciones en proporción al tamaño de la población. Sin crecimiento, esto da un decaimiento
    exponencial.
    """

    nombre = 'Constante'
    cls_ramas = [Q]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        pobs = símismo.pobs(sim)

        # Tomamos el paso en cuenta según las reglas de probabilidades conjuntas:
        # p(x sucede n veces) = (1 - (1- p(x))^n)
        return pobs * (1 - (1 - cf['q']) ** paso)
