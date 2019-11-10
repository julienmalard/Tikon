import math

from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela
from tikon.result.res import Resultado


class Res1(Resultado):
    nombre = 'res 1'
    unids = None


class Res2(Resultado):
    nombre = 'res 2'
    unids = None


class SimulMóduloCntrl(SimulMódulo):
    resultados = [Res1, Res2]

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        símismo.poner_valor('res 1', math.pi)
        val_1 = símismo.obt_valor('res 1')
        símismo.poner_valor('res 2', val_1)

    def requísitos(símismo, controles=False):
        if controles:
            return ['var']


class MiMódulo(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloCntrl


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo(MiMódulo)
