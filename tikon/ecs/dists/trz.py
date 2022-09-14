from typing import Union, Any, cast

import numpy as np

from tikon.tipos import Tipo_Valor_Numérico, Tipo_Matriz_Numérica
from tikon.ecs.dists.dists import Dist, DicDist


class DicDistTraza(DicDist):
    trz: Tipo_Matriz_Numérica
    pesos: Tipo_Matriz_Numérica


class DistTraza(Dist):
    trz: Tipo_Matriz_Numérica
    pesos: Tipo_Matriz_Numérica

    def __init__(símismo, trz: Tipo_Matriz_Numérica, pesos: Tipo_Matriz_Numérica = None):
        if pesos is None:
            pesos = np.ones_like(trz)
        pesos_finales = pesos / np.sum(pesos)

        if trz.size != pesos_finales.size:
            raise ValueError('El tamaño de la traza y él de sus pesos deben ser iguales.')

        símismo.trz = trz
        símismo.pesos = pesos_finales

    def obt_vals(símismo, n: int) -> Tipo_Matriz_Numérica:
        return np.random.choice(símismo.trz, n, p=símismo.pesos)

    def obt_vals_índ(símismo, í: Union[int, Tipo_Matriz_Numérica]) -> Tipo_Matriz_Numérica:
        return símismo.trz[í]

    def tmñ(símismo) -> int:
        return símismo.trz.size

    def aprox_líms(símismo, prc: Tipo_Valor_Numérico) -> Tipo_Matriz_Numérica:
        # Las superficies de las colas que hay que dejar afuera del rango de los límites
        colas = ((1 - prc) / 2, 0.5 + prc / 2)
        trz, pesos = símismo.trz, símismo.pesos
        return np.array([_centil_pesos(trz, pesos, colas[0]), _centil_pesos(trz, pesos, colas[1])])

    def a_dic(símismo) -> DicDistTraza:
        return DicDistTraza(
            tipo=símismo.__class__.__name__,
            trz=símismo.trz,
            pesos=símismo.pesos
        )

    @classmethod
    def de_dic(cls, dic: DicDist) -> "DistTraza":
        if dic["tipo"] != "DistTraza":
            raise ValueError(dic)
        dicDistTraza = cast(DicDistTraza, dic)
        return DistTraza(trz=dicDistTraza['trz'], pesos=dicDistTraza['pesos'])


def _centil_pesos(x: Tipo_Matriz_Numérica, p: Tipo_Matriz_Numérica, q: float | int) -> Tipo_Matriz_Numérica:
    # Mientras esperemos que numpy lo implemente
    # código de https://github.com/nudomarinero/wquantiles/blob/master/wquantiles.py
    índs_ord = np.argsort(x)
    x_ord = x[índs_ord]
    p_ord = p[índs_ord]

    sn = np.cumsum(p_ord)
    pn = (sn - 0.5 * p_ord) / sn[-1]
    return np.interp(q, pn, x_ord)
