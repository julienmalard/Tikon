from tikon.ecs.árb_mód import Parám

from .._plntll import EcuaciónOrg


class A(Parám):
    nombre = 'a'
    líms = (0, None)
    unids = None


class Constante(EcuaciónOrg):
    """
    Reproducciones en proporción al tamaño de la población.
    """

    nombre = 'Constante'
    cls_ramas = [A]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        return cf['a'] * símismo.pobs(sim) * paso
