from warnings import warn as avisar

import numpy as np
from tikon.ecs.dists.dists import Dist


class DistTraza(Dist):
    def __init__(símismo, trz, pesos=None):
        if pesos is None:
            pesos = np.ones_like(trz)
        else:
            pesos = pesos / np.sum(pesos)

        if trz.size != pesos.size:
            raise ValueError

        símismo.trz = trz
        símismo.pesos = pesos

    def obt_vals(símismo, n):
        reemplazar = n > len(símismo.trz)
        if reemplazar:
            avisar('Repitiendo valores porque se pidieron más repeticiones que hay disponibles.')
        return np.random.choice(símismo.trz, n, replace=reemplazar, p=símismo.pesos)

    def obt_vals_índ(símismo, í):
        return símismo.trz[í]

    def tmñ(símismo):
        return símismo.trz.size

    def aprox_líms(símismo, prc):
        # Las superficies de las colas que hay que dejar afuera del rango de los límites
        colas = ((1 - prc) / 2, 0.5 + prc / 2)

        return np.array([np.percentile(símismo.trz, colas[0] * 100, np.percentile(símismo.trz, colas[1] * 100))])

    def a_dic(símismo):
        return {
            'tipo': símismo.__class__.__name__,
            'trz': símismo.trz,
            'pesos': símismo.pesos
        }

    @classmethod
    def de_dic(cls, dic):
        return DistTraza(trz=dic['trz'], pesos=dic['pesos'])
