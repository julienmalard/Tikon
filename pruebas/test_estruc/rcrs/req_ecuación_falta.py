from tikon.ecs import ÁrbolEcs, CategEc, SubcategEc, Ecuación, EcuaciónVacía
from tikon.estruc import Módulo, SimulMódulo, Exper, Parcela, Modelo, Coso


class EcuaciónReqFalta(Ecuación):
    nombre = 'req falta'

    def eval(símismo, paso, sim):
        pass

    def requísitos(símismo, controles=False):
        if not controles:
            return ['otro modelo.no existo']


class EcuaciónReqControlesFalta(Ecuación):
    nombre = 'req controles falta'

    def eval(símismo, paso, sim):
        pass

    def requísitos(símismo, controles=False):
        if controles:
            return ['no existo']


class SubCategReqFalta(SubcategEc):
    nombre = 'subcateg'
    cls_ramas = [EcuaciónVacía, EcuaciónReqFalta, EcuaciónReqControlesFalta]


class CategReqFalta(CategEc):
    nombre = 'categ'
    cls_ramas = [SubCategReqFalta]


class EcsReqFalta(ÁrbolEcs):
    nombre = 'Ecs requísito falta'
    cls_ramas = [CategReqFalta]


class CosoReqEcFalta(Coso):

    def __init__(símismo, nombre):
        super().__init__(nombre, EcsReqFalta)


class SimulMóduloReqEcFalta(SimulMódulo):
    pass


coso = CosoReqEcFalta('Ütz awäch')


class MóduloReqEcFalta(Módulo):
    nombre = 'Requísitos ecs faltan'
    cls_simul = SimulMóduloReqEcFalta
    cls_ecs = EcsReqFalta

    def __init__(símismo):
        super().__init__(cosos=coso)


exper = Exper('exper', Parcela('parcela'))
modelo = Modelo(MóduloReqEcFalta())
