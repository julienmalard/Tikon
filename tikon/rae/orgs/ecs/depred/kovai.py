import numpy as np

from tikon.ecs.árb_mód import Parám
from tikon.rae.orgs.ecs.depred._plntll_ec import EcuaciónDepred
from tikon.rae.orgs.ecs.utils import probs_conj


class PrAKovai(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']


class PrBKovai(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class Kovai(EcuaciónDepred):
    """
    Depredación de respuesta funcional de asíntota doble (ecuación Kovai).
    y = a*(1 - e^(-u/(a*D))); u = P + e^(-P/b) - b

      a es el máximo de consumo de presa por depredador (cuando las presas son abundantes y los
        depredadores no compiten entre sí mismos)

      b es la densidad de presas a la cuál, donde hay suficientemente pocos depredadores para causar
        competition entre ellos, los depredadores consumirán a/e presas por depredador.

    """
    nombre = 'Kovai'
    cls_ramas = [PrAKovai, PrBKovai]

    def eval(símismo, paso):
        dens = símismo.obt_dens_pobs(filtrar=False)
        cf = símismo.cf

        #
        dens_depred = símismo.obt_dens_pobs(eje_extra='víctima')  # La población de esta etapa (depredador)

        presa_efec = np.add(
            dens,
            np.multiply(cf['b'], np.subtract(np.exp(
                np.divide(-dens, cf['b'])
            ), 1)),
        )
        ratio = presa_efec / dens_depred

        depred_etp = np.multiply(
            cf['a'],
            np.subtract(
                1,
                np.exp(
                    np.divide(
                        -np.where(ratio == np.inf, [0], ratio),
                        cf['a']
                    )
                )
            )
        )

        # Ajustar por la presencia de múltiples presas (según eje presas)
        eje_presas = símismo.í_eje_res('víctima')
        probs_conj(depred_etp, pesos=cf['a'], máx=1, eje=eje_presas)

        return depred_etp
