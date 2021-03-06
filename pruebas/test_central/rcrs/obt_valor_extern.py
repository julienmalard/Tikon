from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela
from tikon.central.res import Resultado


class Res1(Resultado):
    nombre = 'res 1'
    unids = None


class SimulMódulo1(SimulMódulo):
    resultados = [Res1]

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        símismo.poner_valor('res 1', 2)


class Res2(Resultado):
    nombre = 'res 2'
    unids = None


class SimulMódulo2(SimulMódulo):
    resultados = [Res2]

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        val = símismo.obt_valor_extern('módulo 1.res 1')
        símismo.poner_valor('res 2', val)


class Módulo1(Módulo):
    nombre = 'módulo 1'
    cls_simul = SimulMódulo1


class Módulo2(Módulo):
    nombre = 'módulo 2'
    cls_simul = SimulMódulo2


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo([Módulo1(), Módulo2()])
