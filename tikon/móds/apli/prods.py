from tikon.estruc.coso import Coso

from .ecs import EcsProducto


class Producto(Coso):
    def __init__(símismo, nombre):
        super().__init__(nombre, ecs=EcsProducto)
