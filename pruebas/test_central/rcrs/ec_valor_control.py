from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela, Coso
from tikon.central.res import Resultado
from tikon.ecs import ÁrbolEcs, CategEc, Ecuación, SubcategEc, EcuaciónVacía


class EcuaciónObtVal(Ecuación):
    nombre = 'obt val'
    eje_cosos = 'coso'

    def eval(símismo, paso, sim):
        val = símismo.obt_valor_control(sim, 'var control')
        símismo.poner_valor_mód(sim, 'res', val)


class SubCategObtVal(SubcategEc):
    nombre = 'subcateg'
    cls_ramas = [EcuaciónObtVal, EcuaciónVacía]
    eje_cosos = 'coso'


class CategObtVal(CategEc):
    nombre = 'categ'
    cls_ramas = [SubCategObtVal]
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


class Res(ResEjeCoso):
    nombre = 'res'


class SimulMóduloObtVal(SimulMódulo):
    resultados = [Res]

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)


coso = CosoObtValor('hola')


class MóduloObtVal(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloObtVal

    def __init__(símismo, cosos=None):
        símismo.l_cosos = cosos
        super().__init__(cosos)

    def gen_ecs(símismo, modelo, mód, exper, n_reps):
        return EcsObtVal(modelo, mód, exper, cosos=símismo.l_cosos, n_reps=n_reps)


mi_exper = Exper('exper', Parcela('parcela'))
mi_modelo = Modelo(MóduloObtVal([coso]))
