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
            raise ValueError('El tamaño de la traza y él de sus pesos deben ser iguales.')

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
        trz, pesos = símismo.trz, símismo.pesos
        return np.array([_centil_pesos(trz, pesos, colas[0]), _centil_pesos(trz, pesos, colas[1])])

    def a_dic(símismo):
        return {
            'tipo': símismo.__class__.__name__,
            'trz': símismo.trz,
            'pesos': símismo.pesos
        }

    @classmethod
    def de_dic(cls, dic):
        return DistTraza(trz=dic['trz'], pesos=dic['pesos'])


def _centil_pesos(x, p, q):
    # Mientras esparamos que numpy lo implemente
    # código de https://github.com/nudomarinero/wquantiles/blob/master/wquantiles.py
    índs_ord = np.argsort(x)
    x_ord = x[índs_ord]
    p_ord = p[índs_ord]

    sn = np.cumsum(p_ord)
    pn = (sn - 0.5 * p_ord) / sn[-1]
    return np.interp(q, pn, x_ord)
