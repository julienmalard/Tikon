from tikon.central.coso import Coso

from .ecs import EcsTrampa


class Trampa(Coso):
    def __init__(símismo, nombre):
        super().__init__(nombre, ecs=EcsTrampa)
