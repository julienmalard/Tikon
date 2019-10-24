from tikon.ecs.árb_mód import SubcategEc, EcuaciónVacía
from tikon.móds.rae.red_ae.utils import EJE_ETAPA, RES_CREC

from .const import Constante
from .expon import Expon
from .logíst import Logíst
from .logíst_depred import LogístDepred
from .logíst_presa import LogístPresa


class EcuaciónCrec(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [EcuaciónVacía, Expon, Logíst, LogístPresa, LogístDepred, Constante]
    _nombre_res = RES_CREC
    _eje_cosos = EJE_ETAPA
