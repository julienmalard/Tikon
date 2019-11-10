from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela


class SimulMóduloCntrlFalta(SimulMódulo):
    def requísitos(símismo, controles=False):
        if controles:
            return ['Yo no son un variable de control.']


class MóduloCntrlFalta(Módulo):
    nombre = 'Control falta'
    cls_simul = SimulMóduloCntrlFalta


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo(MóduloCntrlFalta())
