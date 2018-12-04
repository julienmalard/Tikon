import numpy as np

from tikon.ecs.estruc import CategEc, SubCategEc, Ecuación, EcuaciónVacía, Parám, FuncEc


class Constante(FuncEc):
    """
    Muertes en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición exponencial.
    """

    def __call__(self, cf, paso, mnjdr_móds):
        return np.multiply(pob_etp, cf['q'])  # para hacer: arreglar índices pobs


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


inf = np.inf

ecs_muert = CategEc(
    'Muertes',
    subs=[
        SubCategEc(
            'Ecuación',
            ecs=[
                EcuaciónVacía(),
                Ecuación(
                    'Constante',
                    paráms=[
                        Parám('q', (0, 1))
                    ],
                    fun=Constante
                ),
                Ecuación(
                    'Log Normal Temperatura',
                    paráms=[
                        Parám('t', (-inf, inf)),
                        Parám('p', (0, inf))
                    ],
                    fun=LogNormalTemperatura
                ),
                Ecuación(
                    'Asimptótico Humedad',
                    paráms=[
                        Parám('a', (0, inf)),
                        Parám('b', (-inf, inf))
                    ],
                    fun=AsimptóticoHumedad
                ),
                Ecuación(
                    'Sigmoidal Temperatura',
                    paráms=[
                        Parám('a', (-inf, inf)),
                        Parám('b', (0, inf))
                    ],
                    fun=SigmoidalTemperatura
                )
            ]
        )
    ]
)
