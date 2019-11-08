from .parc import _controles_parc

_controles_auto = {
    'n_cohortes': 10
}


class ControlesExper(object):
    def __init__(símismo, parcelas):
        símismo._auto = _controles_auto
        símismo._usuario = {}

        símismo._usuario.update(_controles_parc(parcelas))

    def __contains__(símismo, itema):
        return itema in símismo._auto or itema in símismo._usuario

    def __setitem__(símismo, llave, valor):
        if valor is not None:
            símismo._usuario[llave] = valor
        else:
            if llave in símismo._usuario:
                símismo._usuario.pop(llave)

    def __getitem__(símismo, itema):
        try:
            return símismo._usuario[itema]
        except KeyError:
            return símismo._auto[itema]
