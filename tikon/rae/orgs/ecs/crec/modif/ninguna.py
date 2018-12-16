from tikon.ecs.árb_mód import Ecuación, Parám


class R(Parám):
    nombre = 'r'
    líms = (0, None)


class Ninguna(Ecuación):
    nombre = 'Ninguna'
    cls_ramas = [R]

    def eval(símismo, paso):
        # Sin modificación a r.
        return símismo.cf['r'] * paso
