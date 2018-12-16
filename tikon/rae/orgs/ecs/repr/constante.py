from tikon.ecs.árb_mód import Ecuación, Parám


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class Constante(Ecuación):
    """
    Reproducciones en proporción al tamaño de la población.
    """

    nombre = 'Constante'
    cls_ramas = [A]

    def eval(símismo, paso):
        cf = símismo.cf
        return cf['a'] * símismo.pobs() * paso
