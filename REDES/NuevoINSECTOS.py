from REDES.ORGANISMO import Organismo


class Insecto(Organismo):
    def __init__(símismo, nombre, huevo, njuvenil, pupa, adulto, tipo_ecuaciones):

        super().__init__(nombre=nombre)


# Unas clases prehechas para simplificar la creación de insectos
class Simple(Insecto):
    def __init__(self, nombre, huevo=False, tipo_ecuaciones='capacidad_de_carga'):
        super().__init__(nombre=nombre, huevo=huevo, njuvenil=0, pupa=False, adulto=True,
                         tipo_ecuaciones=tipo_ecuaciones)


class MetamCompleta(Insecto):
    def __init__(self, nombre, huevo=True, njuvenil=1, adulto=True):
        super().__init__(nombre=nombre, huevo=huevo, njuvenil=njuvenil, pupa=True, adulto=adulto,
                         tipo_ecuaciones='etapas')


class MetamIncompleta(Insecto):
    def __init__(self, nombre, huevo=True, njuvenil=1, adulto=True):
        super().__init__(nombre=nombre,  huevo=huevo, njuvenil=njuvenil, pupa=False, adulto=adulto,
                         tipo_ecuaciones='etapas')
