from tikon.exper.parc import _controles_parc

_controles_auto = {
    'n_cohortes': 10
}


class ControlesExper(object):
    def __init__(símismo, parcelas):
        símismo._auto = _controles_auto
        símismo._usuario = {}

        símismo._usuario.update(_controles_parc(parcelas))

    def verif(símismo):
        pass

    def __setitem__(símismo, llave, valor):
        símismo._usuario[llave] = valor

    def __getitem__(símismo, itema):
        try:
            return símismo._usuario[itema]
        except KeyError:
            return símismo._auto[itema]
