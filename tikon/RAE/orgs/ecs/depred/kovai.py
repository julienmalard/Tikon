import numpy as np

from tikon.RAE.red_ae.utils import probs_conj
from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class PrAKovai(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']


class PrBKovai(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class Kovai(Ecuación):
    """
    Depredación de respuesta funcional de asíntota doble (ecuación Kovai).
    y = a*(1 - e^(-u/(a*D))); u = P + e^(-P/b) - b

      a es el máximo de consumo de presa por depredador (cuando las presas son abundantes y los
        depredadores no compiten entre sí mismos)

      b es la densidad de presas a la cuál, donde hay suficientemente pocos depredadores para causar
        competition entre ellos, los depredadores consumirán a/e presas por depredador.

    """
    nombre = 'Kovai'
    _cls_ramas = [PrAKovai, PrBKovai]

    def __call__(símismo, paso):
        dens = símismo.obt_val_mód('Dens', índs=símismo._í_cosos)
        cf = símismo.cf

        #
        dens_depred = dens[:, :, :, 0, í_etps, np.newaxis]  # La población de esta etapa (depredador)

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
        eje_presas = símismo.í_eje('presa')
        probs_conj(depred_etp, pesos=cf['a'], máx=1, eje=eje_presas)

        return depred_etp
