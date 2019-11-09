import math

from tikon.estruc import Módulo, SimulMódulo, Modelo, Exper, Parcela
from tikon.result.res import Resultado

const = math.e


class Res1(Resultado):
    nombre = 'res 1'
    unids = None


class SimulMódulo1(SimulMódulo):
    resultados = [Res1]


class SimulMódulo2(SimulMódulo):
    def incrementar(símismo, paso, f):
        símismo.poner_valor_extern('módulo 1.res 1', const)


class Módulo1(Módulo):
    nombre = 'módulo 1'
    cls_simul = SimulMódulo1


class Módulo2(Módulo):
    nombre = 'módulo 2'
    cls_simul = SimulMódulo2


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo([Módulo1, Módulo2])
