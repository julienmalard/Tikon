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
        decomp = símismo.obt_res(filtrar=False)  # para hacer: filtara=False debería ser automático para CategEc

        símismo.poner_val_mód(RES_CONC, -decomp, rel=True)
