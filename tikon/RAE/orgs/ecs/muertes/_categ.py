import numpy as np

from tikon.ecs.árb_mód import CategEc, SubcategEc, Ecuación, EcuaciónVacía
from tikon.ecs.paráms import Parám
from .constante import Constante


class LogNormalTemperatura(FuncEc):
    """
    Muertes dependientes en la temperatura, calculadas con la ecuación mencionada en:

    Sunghoon Baek, Youngsoo Son, Yong-Lak Park. 2014. Temperature-dependent development and survival of
      Podisus maculiventris (Hemiptera: Pentatomidae): implications for mass rearing and biological
      control. Journal of Pest Science 87(2): 331-340.

    """
    def __call__(self, cf, paso, mnjdr_móds):
        sobrevivencia = np.exp(-0.5 * (np.log(mnjdr_móds['clima.temp_máx'] / cf['t']) / cf['p']) ** 2)
        return np.multiply(pob_etp, (1 - sobrevivencia))


class AsimptóticoHumedad(FuncEc):
    """
    M. P. Lepage, G. Bourgeois, J. Brodeur, G. Boivin. 2012. Effect of Soil Temperature and Moisture on
    Survival of Eggs and First-Instar Larvae of Delia radicum. Environmental Entomology 41(1): 159-165.
    """
    def __call__(self, cf, paso, mnjdr_móds):
        sobrevivencia = np.maximum(0, np.subtract(1, np.exp(-cf['a'] * (mnjdr_móds['clima.humedad'] - cf['b']))))
        return np.multiply(pob_etp, (1 - sobrevivencia))


class SigmoidalTemperatura(FuncEc):
    """

    """
    def __call__(self, cf, paso, mnjdr_móds):
        sobrevivencia = 1 / (1 + np.exp((mnjdr_móds['clima.temp_máx'] - cf['a']) / cf['b']))
        return np.multiply(pob_etp, (1 - sobrevivencia))


class EcuaciónMuerte(SubcategEc):
    nombre = 'Ecuación'
    _cls_ramas = [EcuaciónVacía, Constante, LogNormalTemperatura, AsimptóticoHumedad, SigmoidalTemperatura]
    auto = Constante

class EcsMuerte(CategEc):
    nombre = 'Muertes'
    _cls_ramas = [EcuaciónMuerte]


Ecuación(
    'Log Normal Temperatura',
    paráms=[
        Parám('t', (None, None)),
        Parám('p', (0, None))
    ],
    fun=LogNormalTemperatura
),
Ecuación(
    'Asimptótico Humedad',
    paráms=[
        Parám('a', (0, None)),
        Parám('b', (None, None))
    ],
    fun=AsimptóticoHumedad
),
Ecuación(
    'Sigmoidal Temperatura',
    paráms=[
        Parám('a', (None, None)),
        Parám('b', (0, None))
    ],
    fun=SigmoidalTemperatura
)
