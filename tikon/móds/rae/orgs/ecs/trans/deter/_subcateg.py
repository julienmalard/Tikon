import numpy as np
from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.utils import RES_TRANS

from .constante import Constante


class TransDeter(SubcategEcOrg):
    """
    Transiciones deteminísticas (y no probabilísticas según la edad)
    """

    nombre = 'Deter'
    cls_ramas = [EcuaciónVacía, Constante]
    _nombre_res = RES_TRANS

    def postproc(símismo, paso, sim):
        trans = símismo.obt_valor_res(sim)
        trans.values[:] = np.floor(trans.values)  # Redondear las transiciones calculadas
        # Quitar los organismos que transicionaron
        símismo.ajust_pobs(sim, -trans)
