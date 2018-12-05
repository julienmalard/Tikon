import numpy as np

from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class T(Parám):
    nombre = 't'
    líms = (None, None)


class P(Parám):
    nombre = 'p'
    líms = (0, None)


class LogNormTemp(Ecuación):
    """
    Muertes dependientes en la temperatura, calculadas con la ecuación mencionada en:

    Sunghoon Baek, Youngsoo Son, Yong-Lak Park. 2014. Temperature-dependent development and survival of
      Podisus maculiventris (Hemiptera: Pentatomidae): implications for mass rearing and biological
      control. Journal of Pest Science 87(2): 331-340.

    """

    nombre = 'Log Normal Temperatura'
    _cls_ramas = [T, P]

    def __call__(símismo, paso):
        sobrevivencia = np.exp(-0.5 * (np.log(mnjdr_móds['clima.temp_máx'] / cf['t']) / cf['p']) ** 2)
        return np.multiply(pob_etp, (1 - sobrevivencia))
