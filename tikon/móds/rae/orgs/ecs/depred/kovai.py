import numpy as np

from tikon.ecs.árb_mód import Parám
from tikon.móds.rae import EcuaciónDepred
from tikon.móds.rae import probs_conj


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
    # y = a*u*(1 - e^(-P/(a*u*D))); u = (1 - e^(-P / b))
    y = a*(1 - e^(-P*u/(a*D))); u = (1 - e^(-P / b))

      a es el máximo de consumo de presa por depredador (cuando las presas son abundantes y los
        depredadores no compiten entre sí mismos)

      b es la densidad de presas a la cuál, donde hay suficientemente pocos depredadores para causar
        competition entre ellos, los depredadores consumirán a * (1 - 1 / e) ≈ 0.63 * a presas por depredador.

    """
    nombre = 'Kovai'
    cls_ramas = [PrAKovai, PrBKovai]

    def eval(símismo, paso):
        dens = símismo.obt_dens_pobs(filtrar=False)
        cf = símismo.cf

        #
        dens_depred = símismo.obt_dens_pobs(eje_extra='víctima')  # La población de esta etapa (depredador)

        u = 1 - np.exp(-dens / cf['b'])

        ratio = dens / dens_depred
        ratio[np.isinf(ratio)] = 0

        depred_etp = cf['a'] * (1 - np.exp(-ratio * u / cf['a']))

        # Ajustar por la presencia de múltiples presas (según eje presas)
        eje_presas = símismo.í_eje_res('víctima')
        probs_conj(depred_etp, pesos=cf['a'], máx=1, eje=eje_presas)

        return depred_etp
