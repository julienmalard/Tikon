from scipy.stats import uniform
from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela, Coso
from tikon.central.res import Resultado
from tikon.ecs import ÁrbolEcs, CategEc, Ecuación, SubcategEc, EcuaciónVacía, Parám
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.dists import líms_dist

apr = uniform(0, 5)
rango = líms_dist(apr)


class A(Parám):
    nombre = 'a'
    unids = None
    líms = (0, None)
    apriori = APrioriDist(apr)


class EcuaciónParám(Ecuación):
    nombre = 'ec'
    eje_cosos = 'coso'
    cls_ramas = [A]

    def eval(símismo, paso, sim):
        símismo.poner_valor_mód(sim, 'res', símismo.cf['a'])


class SubCategParám(SubcategEc):
    nombre = 'subcateg'
    cls_ramas = [EcuaciónParám, EcuaciónVacía]
    eje_cosos = 'coso'


class CategParám(CategEc):
    nombre = 'categ'
    cls_ramas = [SubCategParám]
    eje_cosos = 'coso'


class EcsParám(ÁrbolEcs):
    nombre = 'Ecs obt val'
    cls_ramas = [CategParám]


class CosoParám(Coso):
    def __init__(símismo, nombre):
        super().__init__(nombre, EcsParám)


class Res(Resultado):
    unids = None
    nombre = 'res'

    def __init__(símismo, sim, coords, vars_interés):
        coords = {'coso': sim.ecs.cosos, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)


class SimulMóduloParám(SimulMódulo):
    resultados = [Res]


coso = CosoParám('hola')


class MóduloParám(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloParám
    eje_coso = 'coso'

    def __init__(símismo, cosos=None):
        símismo.l_cosos = cosos
        super().__init__(cosos)

    def gen_ecs(símismo, modelo, mód, n_reps):
        return EcsParám(modelo, mód, cosos=símismo.l_cosos, n_reps=n_reps)


exper = Exper('exper', Parcela('parcela'))
mi_modelo = Modelo(MóduloParám([coso]))
