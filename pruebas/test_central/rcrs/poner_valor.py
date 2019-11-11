from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela
from tikon.central.res import Resultado


class Res(Resultado):
    nombre = 'res'
    unids = None


class SimulMóduloCntrl(SimulMódulo):
    resultados = [Res]

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        super().__init__(mód, simul_exper, ecs, vars_interés)
        símismo.relativo = mód.relativo

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        símismo.poner_valor('res', 1, rel=símismo.relativo)


class MóduloValorControl(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloCntrl

    def __init__(símismo, relativo):
        símismo.relativo = relativo
        super().__init__(cosos=None)


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo(MóduloValorControl(relativo=False))
modelo_rel = Modelo(MóduloValorControl(relativo=True))
