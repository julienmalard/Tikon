from tikon.central import Módulo, SimulMódulo, Exper, Parcela, Modelo


class SimulMóduloNombrePunto(SimulMódulo):
    pass


class MóduloNombrePunto(Módulo):
    nombre = 'Tengo.un.Punto'
    cls_simul = SimulMóduloNombrePunto


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo([MóduloNombrePunto()])
