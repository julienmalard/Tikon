import numpy as np

_controles_auto = {
    'parcelas': ['1'],
    'superficies': np.array([1.]),
    'lat': np.array([11.0025]),
    'lon': np.array([76.9656])
}


class ControlesExper(object):
    def __init__(símismo):
        símismo._usuario = {}
        símismo._auto = _controles_auto

    def verif(símismo):
        pass

    def __setitem__(símismo, llave, valor):
        símismo._usuario[llave] = valor

    def __getitem__(símismo, itema):
        try:
            return símismo._usuario[itema]
        except KeyError:
            return símismo._auto[itema]
