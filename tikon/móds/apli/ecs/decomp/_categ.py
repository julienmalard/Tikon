from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.apli.ecs.utils import ECS_DECOMP
from tikon.móds.apli.utils import EJE_PRODUCTO, RES_DECOMP, RES_CONC

from .exp_neg import DecaiExp


class EcDecomp(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [DecaiExp, EcuaciónVacía]
    _eje_cosos = EJE_PRODUCTO
    _nombre_res = RES_DECOMP


class EcsDescomp(CategEc):
    nombre = ECS_DECOMP
    cls_ramas = [EcDecomp]
    _eje_cosos = EJE_PRODUCTO
    _nombre_res = RES_DECOMP

    def postproc(símismo, paso, sim):
        decomp = símismo.obt_val_res(sim)

        símismo.poner_val_mód(sim, RES_CONC, -decomp, rel=True)
