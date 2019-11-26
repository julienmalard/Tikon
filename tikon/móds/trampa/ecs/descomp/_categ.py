from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.trampa.ecs.utils import ECS_DESCOMP
from tikon.móds.trampa.utils import EJE_TRAMPA, RES_DESCOMP, RES_DENS

from .exp_neg import DecaiExp


class EcDescomp(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [DecaiExp, EcuaciónVacía]
    eje_cosos = EJE_TRAMPA
    _nombre_res = RES_DESCOMP


class EcsDescomp(CategEc):
    nombre = ECS_DESCOMP
    cls_ramas = [EcDescomp]
    eje_cosos = EJE_TRAMPA
    _nombre_res = RES_DESCOMP

    def postproc(símismo, paso, sim):
        descomp = símismo.obt_valor_res(sim)

        símismo.poner_valor_mód(sim, RES_DENS, -descomp, rel=True)
