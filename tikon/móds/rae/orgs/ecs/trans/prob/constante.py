from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg


class Q(Parám):
    nombre = 'q'
    líms = (0, 1)
    unids = None


class Constante(EcuaciónOrg):
    """
    Transiciones en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
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
