from tikon.central import Módulo, SimulMódulo, Exper, Parcela, Modelo


class SimulMóduloDependiente(SimulMódulo):
    def requísitos(símismo, controles=False):
        if not controles:
            return ['Independiente.var 2']


class MóduloDependiente(Módulo):
    nombre = 'Dependiente'
    cls_simul = SimulMóduloDependiente


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo(MóduloDependiente())
