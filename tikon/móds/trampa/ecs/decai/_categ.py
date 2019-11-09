from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.trampa.ecs.utils import ECS_DECAI
from tikon.móds.trampa.utils import EJE_TRAMPA, RES_DECAI, RES_PODER

from .exp_neg import DecaiExp


class EcDecai(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [DecaiExp, EcuaciónVacía]
    _eje_cosos = EJE_TRAMPA
    _nombre_res = RES_DECAI


class EcsDecai(CategEc):
    nombre = ECS_DECAI
    cls_ramas = [EcDecai]
    _eje_cosos = EJE_TRAMPA
    _nombre_res = RES_DECAI

    def postproc(símismo, paso, sim):
        decai = símismo.obt_valor_res(sim)

        símismo.poner_valor_mód(sim, RES_PODER, -decai, rel=True)
