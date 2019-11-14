from tikon.central import Módulo, SimulMódulo, Exper, Parcela, Modelo, Coso, Resultado
from tikon.ecs import ÁrbolEcs, CategEc, SubcategEc, Ecuación, EcuaciónVacía, Parám
from tikon.ecs.paráms import Inter

rango = (1, 3)


class ResInter(Resultado):
    unids = None
    nombre = 'res'

    def __init__(símismo, sim, coords, vars_interés):
        coords = {'coso': sim.ecs.cosos, 'otro': sim.ecs.cosos, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)


class ParámInter(Parám):
    nombre = 'a'
    unids = None
    líms = rango
    inter = ['otro']


class EcuaciónInter(Ecuación):
    nombre = 'ec'
    cls_ramas = [ParámInter]
    eje_cosos = 'coso'
    _nombre_res = 'res'

    def eval(símismo, paso, sim):
        símismo.poner_valor_res(sim, símismo.cf['a'])


class SubCategInter(SubcategEc):
    nombre = 'subcateg'
    cls_ramas = [EcuaciónInter, EcuaciónVacía]
    eje_cosos = 'coso'


class CategInter(CategEc):
    nombre = 'categ'
    cls_ramas = [SubCategInter]
    eje_cosos = 'coso'


class EcsInter(ÁrbolEcs):
    nombre = 'Ecs inter'
    cls_ramas = [CategInter]


class CosoEcInter(Coso):
    def __init__(símismo, nombre):
        super().__init__(nombre, EcsInter)
        símismo.interacciones = []

    def interactua_con(símismo, otro):
        if isinstance(otro, Coso):
            otro = [otro]
        símismo.interacciones += otro


class SimulMóduloEcInter(SimulMódulo):
    resultados = [ResInter]


coso1 = CosoEcInter('Xsaqär tata')
coso2 = CosoEcInter('Ütz awäch')
coso3 = CosoEcInter('Rïn ütz maltyöx')


class MóduloEcInter(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloEcInter
    cls_ecs = EcsInter
    eje_coso = 'coso'

    def __init__(símismo):
        super().__init__(cosos=[coso1, coso2, coso3])

    def inter(símismo, modelo, coso, tipo):
        for tp in tipo:
            if tp == 'otro':
                return Inter(coso.interacciones, eje='otro')


exper = Exper('exper', Parcela('parcela'))
mi_modelo = Modelo(MóduloEcInter())
