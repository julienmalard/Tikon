from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.apli.ecs.utils import ECS_descop
from tikon.móds.apli.utils import EJE_PRODUCTO, RES_descop, RES_CONC

from .exp_neg import DecaiExp


class Ecdescop(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [DecaiExp, EcuaciónVacía]
    _eje_cosos = EJE_PRODUCTO
    _nombre_res = RES_descop


class EcsDescomp(CategEc):
    nombre = ECS_descop
    cls_ramas = [Ecdescop]
    _eje_cosos = EJE_PRODUCTO
    _nombre_res = RES_descop

    def postproc(símismo, paso, sim):
        descop = símismo.obt_val_res(sim)

        símismo.poner_val_mód(sim, RES_CONC, -descop, rel=True)
