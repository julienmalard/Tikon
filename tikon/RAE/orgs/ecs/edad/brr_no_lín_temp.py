import numpy as np

from tikon.ecs.árb_mód import Ecuación, Parám


class PrTDevMínBNLT(Parám):
    nombre = 't_dev_mín'
    líms = (None, None)


class PrTLetalBNLT(Parám):
    nombre = 't_letal'
    líms = (None, None)


class PrMBNLT(Parám):
    nombre = 'm'
    líms = (0, None)


class FuncBrièreNoLinearTemperatura(Ecuación):
    """
    Edad calculada con la taza de desarrollo de la ecuación de temperatura no linear de Briere.

    Youngsoo Son et al. 2012. Estimation of developmental parameters for adult emergence of Gonatocerus
      morgani, a novel egg parasitoid of the glassy-winged sharpshooter, and development of a degree-day
      model. Biological Control 60(3): 233-260.
    """
    nombre = 'Brière No Linear Temperatura'
    cls_ramas = [PrTDevMínBNLT, PrTLetalBNLT, PrMBNLT]

    def eval(símismo, paso):
        mnjdr_móds = símismo.mnjdr_móds
        cf = símismo.cf

        return (mnjdr_móds['clima.temp_prom'] * (mnjdr_móds['clima.temp_prom'] - cf['t_dev_mín']) *
                np.power(cf['t_letal'] - mnjdr_móds['clima.temp_prom'], 1 / cf['m'])) * paso
