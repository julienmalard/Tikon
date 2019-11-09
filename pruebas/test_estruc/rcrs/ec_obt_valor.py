from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela, Coso
from tikon.ecs import ÁrbolEcs, CategEc, Ecuación, SubcategEc, EcuaciónVacía, Parám
from tikon.result.res import Resultado


class EcuaciónObtVal(Ecuación):
    nombre = 'obt val'

    def eval(símismo, paso, sim):
        val = símismo.obt_valor_mód(sim, 'res 1')
        símismo.poner_valor_mód(sim, 'var 2', val)


class SubCategReqFalta(SubcategEc):
    nombre = 'subcateg'
    cls_ramas = [EcuaciónVacía, EcuaciónObtVal]


class CategObtVal(CategEc):
    nombre = 'categ'
    cls_ramas = [SubCategReqFalta]


class EcsObtVal(ÁrbolEcs):
    nombre = 'Ecs obt val'
    cls_ramas = [CategObtVal]


class CosoReqEcFalta(Coso):
    def __init__(símismo, nombre):
        super().__init__(nombre, EcsObtVal)


class Res1(Resultado):
    nombre = 'res 1'
    unids = None


class Res2(Resultado):
    nombre = 'res 2'
    unids = None


class SimulMóduloObtVal(SimulMódulo):
    resultados = [Res1, Res2]


class MóduloObtVal(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloObtVal

    def gen_ecs(símismo, modelo, mód, n_reps):
        return EcsObtVal(símismo.cosos)


exper = Exper('exper', Parcela('parcela'))
mi_modelo = Modelo(MóduloObtVal([coso1, coso2, coso3]))
