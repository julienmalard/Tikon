

class Organismo(object):
    def __init__(símismo, nombre):
        símismo.receta = dict(nombre=nombre,
                              ecuaciones={'Crecimiento': None,
                                          'Depredación': None,
                                          'Movimiento': None})
        símismo.nombre = nombre
        símismo.etapas = []

    def añadir_etapa(símismo, nombre, posición):
        pass

    def quitar_etapa(símismo, nombre, posición):
        pass

    def secome(símismo, otro_org, etps_símismo=None, etps_otro=None):
        pass

    def nosecome(símismo, otro_org, etps_símismo=None, etps_otro=None):
        pass

    def cargar(símismo):
        pass

    def guardar(símismo):
        pass


class Etapa(object):
    pass
