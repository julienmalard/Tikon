from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class R(Parám):
    nombre = 'r'
    líms = (0, None)


class Ninguna(Ecuación):
    nombre = 'Ninguna'
    _cls_ramas = [R]

    def __call__(símismo, paso):
        # Sin modificación a r.
        return símismo.cf['r'] * paso
