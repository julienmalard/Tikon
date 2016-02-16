

class Organismo(object):
    def añadir_etapa(símismo, nombre, posición):
        pass

    def quitar_etapa(símismo, nombre, posición):
        pass



class Insecto(Organismo):
    pass


# Unas clases prehechas para simplificar la creación de insectos
class Simple(Insecto):
    def __init__(self, nombre, huevo=False, tipo_ecuaciones='capacidad_de_carga'):
        super().__init__(nombre=nombre, huevo=huevo, njuvenil=0, adulto=True, tipo_ecuaciones=tipo_ecuaciones)


class MetamCompleta(Insecto):
    def __init__(self, nombre, huevo=True, njuvenil=1, adulto=True):
        super().__init__(nombre=nombre, huevo=huevo, njuvenil=njuvenil, pupa=True, adulto=adulto,
                         tipo_ecuaciones='etapas')


class MetamIncompleta(Insecto):
    def __init__(self, nombre, huevo=True, njuvenil=1, adulto=True):
        super().__init__(nombre=nombre,  huevo=huevo, njuvenil=njuvenil, pupa=False, adulto=adulto,
                         tipo_ecuaciones='etapas')


class Enfermedad(Organismo):
    # ¡Marcela éste es para ti!
    pass


class Etapa(object):
    pass
