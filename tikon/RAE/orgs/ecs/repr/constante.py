from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class Constante(Ecuación):
    """
    Reproducciones en proporción al tamaño de la población.
    """

    nombre = 'Constante'
    _cls_ramas = [A]

    def __call__(símismo, paso):
        cf = símismo.cf
        return cf['a'] * pob_etp * paso
