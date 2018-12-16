import numpy as np

from tikon.ecs.árb_mód import Ecuación, Parám


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class Linear(Ecuación):
    nombre = 'Linear'
    cls_ramas = [A]

    def eval(símismo, paso):
        trans = símismo.obt_res(filtrar=True)
        trans *= símismo.cf['a']
        np.round(trans, out=trans)

        símismo.poner_val_res(trans)
