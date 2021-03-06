from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela
from tikon.central.res import Resultado


class Res(Resultado):
    nombre = 'soy.resultado'
    unids = None


class SimulMóduloVarPunto(SimulMódulo):
    resultados = [Res]


class MóduloVarPunto(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloVarPunto


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo(MóduloVarPunto())
