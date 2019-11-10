from tikon.central import Módulo, SimulMódulo, Exper, Parcela, Modelo


class SimulMóduloDependiente(SimulMódulo):
    def requísitos(símismo, controles=False):
        if not controles:
            return ['Independiente.var 2']


class MóduloDependiente(Módulo):
    nombre = 'Dependiente'
    cls_simul = SimulMóduloDependiente


class SimulMóduloIndependiente(SimulMódulo):
    pass


class MóduloIndependiente(Módulo):
    nombre = 'Independiente'
    cls_simul = SimulMóduloIndependiente


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo([MóduloDependiente(), MóduloIndependiente()])
