from tikon.estruc import Coso

from .ej_ecs import EjÁrbol


class EjemploCoso(Coso):
    def __init__(símismo, nombre='coso'):
        super().__init__(nombre, ecs=EjÁrbol)
