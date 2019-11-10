from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela, Coso
from tikon.ecs import ÁrbolEcs, CategEc, Ecuación, SubcategEc, EcuaciónVacía
from tikon.result.res import Resultado


class EcuaciónObtVal(Ecuación):
    nombre = 'obt val'
    eje_cosos = 'coso'

    def eval(símismo, paso, sim):
        val = símismo.obt_valor_mód(sim, 'res 1')
        símismo.poner_valor_mód(sim, 'res 2', val)


class SubCategReqFalta(SubcategEc):
    nombre = 'subcateg'
    cls_ramas = [EcuaciónObtVal, EcuaciónVacía]
    eje_cosos = 'coso'


class CategObtVal(CategEc):
    nombre = 'categ'
    cls_ramas = [SubCategReqFalta]
    eje_cosos = 'coso'


class EcsObtVal(ÁrbolEcs):
    nombre = 'Ecs obt val'
    cls_ramas = [CategObtVal]


class CosoObtValor(Coso):
    def __init__(símismo, nombre):
        super().__init__(nombre, EcsObtVal)


class ResEjeCoso(Resultado):
    unids = None

    def __init__(símismo, sim, coords, vars_interés):
        coords = {'coso': sim.ecs.cosos, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

    @property
    def nombre(símismo):
        raise NotImplementedError


class Res1(ResEjeCoso):
    nombre = 'res 1'


class Res2(ResEjeCoso):
    nombre = 'res 2'


class SimulMóduloObtVal(SimulMódulo):
    resultados = [Res1, Res2]

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        símismo.poner_valor('res 1', 1, rel=True)


coso1, coso2, coso3 = [CosoObtValor(str(i)) for i in range(1, 4)]


class MóduloObtVal(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloObtVal

    def __init__(símismo, cosos=None):
        símismo.l_cosos = cosos
        super().__init__(cosos)

    def gen_ecs(símismo, modelo, mód, n_reps):
        return EcsObtVal(modelo, mód, cosos=símismo.l_cosos, n_reps=n_reps)


exper = Exper('exper', Parcela('parcela'))
mi_modelo = Modelo(MóduloObtVal([coso1, coso2, coso3]))
