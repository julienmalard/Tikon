import math

from tikon.central import Módulo, SimulMódulo, Exper, Parcela, Modelo, Coso
from tikon.ecs import ÁrbolEcs, CategEc, SubcategEc, Ecuación, EcuaciónVacía
from tikon.central.res import Resultado

agreg_postproc_subcateg = math.pi
agreg_postproc_categ = math.e


class Res(Resultado):
    unids = None
    nombre = 'res'

    def __init__(símismo, sim, coords, vars_interés):
        coords = {'coso': sim.ecs.cosos, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)


class EcuaciónPostProc(Ecuación):
    nombre = 'pp'
    eje_cosos = 'coso'

    def eval(símismo, paso, sim):
        return 1


class EcuaciónNoPostProc(Ecuación):
    nombre = 'npp'
    eje_cosos = 'coso'

    def eval(símismo, paso, sim):
        return 1


class SubCategPostProc(SubcategEc):
    nombre = 'pp'
    cls_ramas = [EcuaciónPostProc, EcuaciónVacía]
    _nombre_res = 'res'
    eje_cosos = 'coso'

    def postproc(símismo, paso, sim):
        vals = símismo.obt_valor_res(sim)
        vals += agreg_postproc_subcateg
        símismo.poner_valor_res(sim, vals)


class SubCategNoPostProc(SubcategEc):
    nombre = 'npp'
    cls_ramas = [EcuaciónNoPostProc, EcuaciónVacía]
    _nombre_res = 'res'
    eje_cosos = 'coso'


class CategPostProc(CategEc):
    nombre = 'categ'
    cls_ramas = [SubCategPostProc, SubCategNoPostProc]
    _nombre_res = 'res'
    eje_cosos = 'coso'

    def postproc(símismo, paso, sim):
        vals = símismo.obt_valor_res(sim, filtrar=True)
        vals += agreg_postproc_categ
        símismo.poner_valor_res(sim, vals)


class EcsPostProc(ÁrbolEcs):
    nombre = 'Ecs requísito falta'
    cls_ramas = [CategPostProc]
    eje_cosos = 'coso'


class CosoPostProc(Coso):
    def __init__(símismo, nombre):
        super().__init__(nombre, EcsPostProc)


class SimulMóduloPostProc(SimulMódulo):
    resultados = [Res]


coso_pp, coso_pp_categ, coso_no_pp = [CosoPostProc(str(i)) for i in range(1, 4)]
coso_pp.activar_ec('categ', subcateg='pp', ec='pp')
coso_pp.desactivar_ec('categ', subcateg='npp')
coso_pp_categ.desactivar_ec('categ', subcateg='pp')
coso_no_pp.desactivar_ec('categ')


class MóduloPostProc(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloPostProc
    cls_ecs = EcsPostProc

    def __init__(símismo):
        super().__init__(cosos=[coso_pp, coso_pp_categ, coso_no_pp])


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo(MóduloPostProc())
