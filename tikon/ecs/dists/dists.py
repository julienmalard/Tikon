from typing import Union, TypedDict, Optional, Iterable, Any

import numpy as np

from tikon.tipos import Tipo_Valor_Numérico, Tipo_Matriz_Núm_Entero, Tipo_Matriz_Numérica

_escala_inf = 1e10
_dist_mu = 1


class DicDist(TypedDict):
    tipo: str


class DicManejadorDists(TypedDict):
    val: Optional[DicDist]
    índices: dict[str, "DicManejadorDists"]


Tipo_Índices = Union[str, Iterable[str]]


class Dist(object):

    def obt_vals(símismo, n: int) -> Tipo_Matriz_Numérica:
        raise NotImplementedError

    def obt_vals_índ(símismo, í: Tipo_Matriz_Núm_Entero) -> Tipo_Matriz_Numérica:
        raise NotImplementedError

    def tmñ(símismo) -> Union[int, float]:
        raise NotImplementedError

    def aprox_líms(símismo, prc: Tipo_Valor_Numérico) -> np.ndarray[Any, np.dtype[np.number]]:
        raise NotImplementedError

    def a_dic(símismo) -> DicDist:
        raise NotImplementedError

    @classmethod
    def de_dic(cls, dic: DicDist) -> "Dist":
        tipo = dic['tipo']
        for x in cls.__subclasses__():
            if x.__name__ == tipo:
                return x.de_dic(dic)

        raise ValueError(tipo)


class ManejadorDists(object):
    val: Optional[Dist]
    índices: dict[str, "ManejadorDists"]

    def __init__(símismo):
        símismo.val = None
        símismo.índices = {}

    def actualizar(símismo, dist: Optional["Dist"], índices: Tipo_Índices = None) -> None:
        índices = símismo._proc_índs(índices)
        if índices is None or not índices:
            símismo.val = dist
        else:
            í = str(índices.pop(0))

            if í not in símismo.índices:
                símismo.índices[í] = ManejadorDists()

            símismo.índices[í].actualizar(dist, índices)

    def obt_val(símismo, índices: Tipo_Índices = None, heredar: bool = True) -> Optional[Dist]:
        índices = símismo._proc_índs(índices)

        if índices is None or not len(índices):
            return símismo.val

        í = str(índices.pop(0))
        if í in símismo.índices:
            return símismo[í].obt_val(índices, heredar)
        if heredar:
            return símismo.val
        return None

    def borrar(símismo, índs: list[str] = None) -> None:
        índs = símismo._proc_índs(índs)

        if índs is None or not índs:
            símismo.val = None
            símismo.índices = {}
        else:
            í = str(índs.pop(0))
            símismo.índices[í].borrar(índs)

    @staticmethod
    def _proc_índs(índs: Optional[Tipo_Índices]) -> Optional[list[str]]:
        if isinstance(índs, str):
            return [índs]
        elif índs is not None:
            return list(índs)  # generar copia
        return None

    def __getitem__(símismo, itema: str) -> "ManejadorDists":
        return símismo.índices[itema]

    def a_dic(símismo) -> DicManejadorDists:
        return {
            'val': símismo.val.a_dic() if símismo.val else None,
            'índices': {str(ll): v.a_dic() for ll, v in símismo.índices.items()}
        }

    @classmethod
    def de_dic(cls, dic: DicManejadorDists, manejador: "ManejadorDists" = None) -> "ManejadorDists":
        if manejador is None:
            manejador = ManejadorDists()

        def act_manejador(
                mnj: ManejadorDists, d: DicManejadorDists, índices_anteriores: list[str] = None
        ) -> None:
            val = d['val']
            índices = d['índices']
            mnj.actualizar(dist=Dist.de_dic(val) if val else None, índices=índices_anteriores)
            for í in índices:
                act_manejador(mnj, d=índices[í], índices_anteriores=(índices_anteriores or []) + [í])

        act_manejador(manejador, d=dic)

        return manejador
