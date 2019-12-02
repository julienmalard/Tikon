import numpy as np
from scipy.stats import expon
from tikon.ecs.aprioris import APrioriDist

from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg


class T(Parám):
    nombre = 't'
    líms = (0, None)
    unids = 'C'
    apriori = APrioriDist(expon(10, scale=20))


class Rho(Parám):
    nombre = 'rho'
    líms = (0, None)
    unids = None
    apriori = APrioriDist(expon(scale=10))


class K(Parám):
    nombre = 'k'
    líms = (0, 1)
    unids = None


class LogNormTemp(EcuaciónOrg):
    """
    Muertes dependientes en la temperatura, calculadas con la ecuación mencionada en [1]_.

    .. math::
       f(x) = k*e^(-0.5*(ln(T/T_m)/\rho)^2)

    Donde `k` es la sobrevivencia máxima a la temperatura optimal `T_m`.

    References
    ----------
    .. [1] Sunghoon Baek, Youngsoo Son, Yong-Lak Park. 2014. Temperature-dependent development and survival of
       Podisus maculiventris (Hemiptera: Pentatomidae): implications for mass rearing and biological
       control. Journal of Pest Science 87(2): 331-340.

    """

    nombre = 'Log Normal Temperatura'
    cls_ramas = [T, Rho, K]

    def eval(símismo, paso, sim):
        cf = símismo.cf

        t_máx = símismo.obt_valor_extern(sim, 'clima.temp_máx')
        sobrevivencia = cf['k'] * np.exp(-0.5 * (np.log(t_máx / cf['t']) / cf['rho']) ** 2)

        return 1 - sobrevivencia

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_máx'}
