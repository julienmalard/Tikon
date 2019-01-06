import numpy as np


class Dims(object):
    def __init__(símismo, coords):
        símismo._coords = coords

        símismo._frm = tuple(crd.tmñ() for crd in símismo._coords.values())

    def frm(símismo):
        return símismo._frm

    def tmñ(símismo):
        return np.prod(símismo._frm)

    def í_eje(símismo, eje):
        return next(i for i, crd in enumerate(símismo._coords) if crd == eje)

    def n_ejes(símismo):
        return len(símismo._coords)

    def _proc_índs(símismo, eje, índs):
        return [í if isinstance(í, int) else símismo._coords[eje].índice(í) for í in índs]

    def rebanar(símismo, índs):
        ejes_índs = {símismo.í_eje(eje): símismo._proc_índs(eje, í) for eje, í in índs.items()}
        return tuple(ejes_índs[e] if e in ejes_índs else slice(None) for e in range(símismo.n_ejes()))

    def __add__(símismo, otro):
        if isinstance(otro, Dims):
            coords_otro = otro._coords
        else:
            coords_otro = otro
        coords = símismo._coords.copy()
        coords.update(coords_otro)
        return Dims(coords)

    def __radd__(símismo, otro):
        if isinstance(otro, dict):
            otro = Dims(otro)
        return otro + símismo


class Coord(object):
    def __init__(símismo, índs):
        símismo.índs = índs

    def tmñ(símismo):
        if isinstance(símismo.índs, int):
            return símismo.índs
        else:
            return len(símismo.índs)

    def índice(símismo, itema):
        return símismo.índs.index(itema)
