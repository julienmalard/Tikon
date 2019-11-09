from tikon.estruc import Módulo, SimulMódulo, Modelo, Exper, Parcela
from tikon.result.res import Resultado


class Res(Resultado):
    nombre = 'res'
    unids = None


class SimulMóduloCntrl(SimulMódulo):
    resultados = [Res]

    def incrementar(símismo, paso, f):
        val_cntrl = símismo.obt_valor_control('var')
        símismo.poner_valor('res', val_cntrl)

    def requísitos(símismo, controles=False):
        if controles:
            return ['var']


class MóduloValorControl(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloCntrl


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo(MóduloValorControl())
