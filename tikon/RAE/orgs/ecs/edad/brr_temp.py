import numpy as np

from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class PrTDevMínBT(Parám):
    nombre = 't_dev_mín'
    líms = (None, None)


class PrTLetalBT(Parám):
    nombre = 't_letal'
    líms = (None, None)


class FuncBrièreTemperatura(Ecuación):
    """
    Edad calculada con la taza de desarrollo de la ecuación de temperatura Brère [1]_. En esta ecuación,
    tal como en las otras con taza de desarrollo, quitamos el parámetro típicamente multiplicado por
    toda la ecuación, porque eso duplicaría el propósito del parámetro de ubicación de las distribuciones
    de probabilidad empleadas después.

    .. [1] Mokhtar, Abrul Monim y Salem Saif al Nabhani. 2010. Temperature-dependent development of dubas bug,
        Ommatissus lybicus (Hemiptera: Tropiduchidae), an endemic pest of date palm, Phoenix dactylifera.
        Eur. J. Entomol. 107: 681–685.
    """
    nombre = 'Brière Temperatura'
    _cls_ramas = [PrTDevMínBT, PrTLetalBT]

    def __call__(símismo, paso):
        mnjdr_móds = símismo.mnjdr_móds
        cf = símismo.cf

        return (mnjdr_móds['clima.temp_prom'] * (mnjdr_móds['clima.temp_prom'] - cf['t_dev_mín']) *
                np.sqrt(cf['t_letal'] - mnjdr_móds['clima.temp_prom'])
                ) * paso
