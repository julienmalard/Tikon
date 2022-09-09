from tikon.central import Módulo, SimulMódulo, Exper, Parcela
from tikon.central.res import Resultado
from tikon.central.matriz import donde as f_donde
from tikon.móds.manejo import Acción
from tikon.móds.manejo.conds import CondVariable


class Res1(Resultado):
    nombre = 'res 1'
    unids = None


class Res2(Resultado):
    nombre = 'res 2'
    unids = None


class EstabRes2(Acción):
    def __init__(símismo, valor):
        símismo.valor = valor

    def __call__(símismo, sim, donde):
        cambio = f_donde(donde, símismo.valor, 0)
        sim['módulo'].poner_valor(var='res 2', val=cambio)


class AgregarRes2(Acción):
    def __init__(símismo, valor):
        símismo.valor = valor

    def __call__(símismo, sim, donde):
        cambio = f_donde(donde, símismo.valor, 0)
        sim['módulo'].poner_valor(var='res 2', val=cambio, rel=True)


class CondReq(CondVariable):
    def requísitos(símismo, controles=False):
        if controles:
            return {'var'}


class AcciónReq(EstabRes2):
    def requísitos(símismo, controles=False):
        if controles:
            return {'var'}


class SimulMóduloCntrl(SimulMódulo):
    resultados = [Res1, Res2]

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        símismo.poner_valor('res 1', 1, rel=True)


class MiMódulo(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloCntrl


exper = Exper('exper', Parcela('parcela'))
