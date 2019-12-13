import numpy as np

from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs.utils import probs_conj
from tikon.móds.rae.utils import EJE_VÍCTIMA, EJE_ETAPA
from ._plntll_ec import EcuaciónDepred


class PrAKovai(Parám):
    nombre = 'a'
    líms = (0, None)
    unids = 'presa / depredador / día'
    inter = ['presa', 'huésped']


class PrBKovai(Parám):
    nombre = 'b'
    líms = (0, None)
    unids = 'presa / ha'
    inter = ['presa', 'huésped']


class Kovai(EcuaciónDepred):
    """
    Depredación de respuesta funcional de asíntota doble (ecuación Kovai).

    .. math::
       f(P, D) = a*(1 - e^(-P*u/(a*D))); u = 1 - (b / P)*(1 - e^(-P / b))

    - f(P, D) es el consumo de presas por depredador por día (ajustamos por el paso después)
    - P es la densidad de presas
    - D es la densidad de depredadores
    - a es el máximo de consumo de presa por depredador (cuando las presas son abundantes y los
      depredadores no compiten entre sí mismos)
    - b es la densidad de presas a la cuál su disponibilidad efectiva para los depredadores es de :math:`1 / e ≈ 0.367`.

    """
    nombre = 'Kovai'
    cls_ramas = [PrAKovai, PrBKovai]

    def eval(símismo, paso, sim):
        dens = símismo.dens_pobs(sim, filtrar=False).renombrar({EJE_ETAPA: EJE_VÍCTIMA})
        cf = símismo.cf

        # La población de esta etapa (depredador)
        dens_depred = símismo.dens_pobs(sim)

        b_sobre_dens = (cf['b'] / dens).llenar_inf(0).llenar_nan(0)
        u = (1 - b_sobre_dens * (1 - (-1/b_sobre_dens).f(np.exp)))

        ratio = (dens / dens_depred).llenar_nan(0)

        depred_etp = cf['a'] * (1 - (-ratio * u / (cf['a'])).fi(np.exp))

        # Ajustar por la presencia de múltiples presas (según eje presas)
        depred_etp = probs_conj(depred_etp, dim=EJE_VÍCTIMA, pesos=cf['a'], máx=1)

        return depred_etp
