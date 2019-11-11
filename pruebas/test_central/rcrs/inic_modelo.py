from tikon.central import Módulo, SimulMódulo, Exper, Parcela
from tikon.central.res import Resultado


class Res1(Resultado):
    nombre = 'res 1'
    unids = None


class SimulMódulo1(SimulMódulo):
    resultados = [Res1]


class Res2(Resultado):
    nombre = 'res 2'
    unids = None


class SimulMódulo2(SimulMódulo):
    resultados = [Res2]


class Módulo1(Módulo):
    nombre = 'módulo 1'
    cls_simul = SimulMódulo1


class Módulo2(Módulo):
    nombre = 'módulo 2'
    cls_simul = SimulMódulo2


exper = Exper('exper', Parcela('parcela'))
