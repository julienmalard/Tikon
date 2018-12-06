import numpy as np

from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class T(Parám):
    nombre = 't'
    líms = (0, None)


class P(Parám):
    nombre = 'p'
    líms = (0, None)


class LogNormTemp(Ecuación):
    nombre = 'Log Normal Temperatura'

    def __call__(símismo, paso):
        # r responde a la temperatura con una ecuación log normal.
        temp_máx = símismo.mnjdr_móds.obt_val_extern('clima.temp_máx')
        cf = símismo.cf

        return np.multiply(
            cf['r'] * paso,
            np.exp(-0.5 * (np.log(temp_máx / cf['t']) / cf['p']) ** 2)
        )
