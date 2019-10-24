from tikon.ecs.árb_mód import SubcategEc, EcuaciónVacía
from .linear import Linear


class MultTrans(SubcategEc):
    """
    Posibilidades de transiciones multiplicadoras (por ejemplo, la eclosión de parasitoides).
    """

    nombre = 'Mult'
    cls_ramas = [EcuaciónVacía, Linear]
    _nombre_res = TRANS
    _eje_cosos = EJE_ETAPA
