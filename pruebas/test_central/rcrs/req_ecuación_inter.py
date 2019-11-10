from tikon.ecs import ÁrbolEcs, CategEc, SubcategEc, Ecuación, EcuaciónVacía, Parám
from tikon.central import Módulo, SimulMódulo, Exper, Parcela, Modelo, Coso
from tikon.ecs.paráms import Inter


class ParámInter(Parám):
    nombre = 'a'
    unids = None
    inter = ['otro']


class EcuaciónReq(Ecuación):
    nombre = 'req'
    cls_ramas = [ParámInter]

    def eval(símismo, paso, sim):
        pass

    def requísitos(símismo, controles=False):
        if controles:
            return ['requísito control']


class SubCategReqInter(SubcategEc):
    nombre = 'subcateg'
    cls_ramas = [EcuaciónReq, EcuaciónVacía]


class CategReqInter(CategEc):
    nombre = 'categ'
    cls_ramas = [SubCategReqInter]


class EcsReqInter(ÁrbolEcs):
    nombre = 'Ecs inter con requísitos'
    cls_ramas = [CategReqInter]


class CosoReqEcInter(Coso):
    def __init__(símismo, nombre):
        super().__init__(nombre, EcsReqInter)
        símismo.interacciones = []

    def interactua_con(símismo, otro):
        símismo.interacciones.append(otro)


class SimulMóduloReqEcInter(SimulMódulo):
    pass


coso1 = CosoReqEcInter('Xsaqär tata')
coso2 = CosoReqEcInter('Ütz awäch')


class MóduloReqEcInter(Módulo):
    nombre = 'Requísitos ecs inter'
    cls_simul = SimulMóduloReqEcInter
    cls_ecs = EcsReqInter
    eje_coso = 'coso'

    def __init__(símismo):
        super().__init__(cosos=[coso1, coso2])

    def inter(símismo, modelo, coso, tipo):
        for tp in tipo:
            if tp == 'otro':
                return Inter(coso.interacciones, eje='eje interacción')


exper = Exper('exper', Parcela('parcela'))
mi_modelo = Modelo(MóduloReqEcInter())
