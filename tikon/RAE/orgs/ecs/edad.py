import numpy as np

from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import CategEc, SubcategEc, Ecuación, EcuaciónVacía
from ...red_ae.utils import días_grados

inf = np.inf


class FuncDías(Ecuación):
    """
    Edad por día.
    """
    nombre = 'Días'

    def __call__(self, paso):
        return paso


class PrMínDG(Parám):
    nombre = 'mín'
    líms = (-inf, inf)


class PrMáxDG(Parám):
    nombre = 'máx'
    líms = (-inf, inf)


class FuncDíasGrados(Ecuación):
    """
    Edad calculada por días grados.
    """
    nombre = 'Días grados'
    _cls_ramas = [PrMínDG, PrMáxDG]

    def __call__(símismo, paso):
        mnjdr_móds = símismo.mnjdr_móds
        cf = símismo.cf

        return días_grados(
            mnjdr_móds['clima.temp_máx'], mnjdr_móds['clima.temp_mín'],
            umbrales=(cf['mín'], cf['máx'])
        ) * paso


class PrTDevMínBT(Parám):
    nombre = 't_dev_mín'
    líms = (-inf, inf)


class PrTLetalBT(Parám):
    nombre = 't_letal'
    líms = (-inf, inf)


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


class PrRhoLT(Parám):
    nombre = 'rho'
    líms = (0, 1)


class PrDeltaLT(Parám):
    nombre = 'delta'
    líms = (0, 1)


class PrTLetalLT(Parám):
    nombre = 't_letal'
    líms = (-inf, inf)


class FuncLoganTemperatura(Ecuación):
    """
    Edad calculada con la taza de desarrollo de la ecuación de temperatura Logan:

    Youngsoo Son y Lewis, Edwin E. 2005. Modelling temperature-dependent development and survival of
      Otiorhynchus sulcatus (Coleoptera: Curculionidae). Agricultural and Forest Entomology 7(3): 201–209.
    """
    nombre = 'Logan Temperatura'
    _cls_ramas = [PrDeltaLT, PrTLetalLT]

    def __call__(símismo, paso):
        mnjdr_móds = símismo.mnjdr_móds
        cf = símismo.cf

        return (np.exp(cf['rho'] * mnjdr_móds['clima.temp_prom']) -
                np.exp(cf['rho'] * cf['t_letal'] - (cf['t_letal'] - mnjdr_móds['clima.temp_prom']) / cf['delta'])
                ) * paso


class PrTDevMínBNLT(Parám):
    nombre = 't_dev_mín'
    líms = (-inf, inf)


class PrTLetalBNLT(Parám):
    nombre = 't_letal'
    líms = (-inf, inf)


class PrMBNLT(Parám):
    nombre = 'm'
    líms = (0, inf)


class FuncBrièreNoLinearTemperatura(Ecuación):
    """
    Edad calculada con la taza de desarrollo de la ecuación de temperatura no linear de Briere.

    Youngsoo Son et al. 2012. Estimation of developmental parameters for adult emergence of Gonatocerus
      morgani, a novel egg parasitoid of the glassy-winged sharpshooter, and development of a degree-day
      model. Biological Control 60(3): 233-260.
    """
    nombre = 'Brière No Linear Temperatura'
    _cls_ramas = [PrTDevMínBNLT, PrTLetalBNLT, PrMBNLT]

    def __call__(símismo, paso):
        mnjdr_móds = símismo.mnjdr_móds
        cf = símismo.cf

        return (mnjdr_móds['clima.temp_prom'] * (mnjdr_móds['clima.temp_prom'] - cf['t_dev_mín']) *
                np.power(cf['t_letal'] - mnjdr_móds['clima.temp_prom'], 1 / cf['m'])) * paso


class EcuaciónEdad(SubcategEc):
    nombre = 'Ecuación'
    _cls_ramas = [
        EcuaciónVacía,
        FuncDías, FuncDíasGrados, FuncBrièreTemperatura, FuncLoganTemperatura, FuncBrièreNoLinearTemperatura
    ]


class EcsEdad(CategEc):
    nombre = 'Edad'
    _cls_ramas = [EcuaciónEdad]
