import numpy as np

from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.rae.orgs.utils import REPR, ETAPA

from .cauchy import Cauchy
from .constante import Constante
from .depred import Depred
from .gamma import Gamma
from .logística import Logística
from .normal import Normal
from .t import T
from .triang import Triang


class ProbRepr(SubcategEc):
    nombre = 'Prob'
    cls_ramas = [EcuaciónVacía, Constante, Depred, Normal, Triang, Cauchy, Gamma, Logística, T]
    auto = Constante
    _nombre_res = REPR
    _eje_cosos = ETAPA

    def postproc(símismo, paso):
        # Agregar las reproducciones a las poblaciones
        reprod = símismo.obt_res(filtrar=False)
        np.round(reprod, out=reprod)
        símismo.poner_val_res(reprod)

        símismo.sim.agregar_pobs(reprod, etapas=símismo.sim.etps_repr)


class EcsRepr(CategEc):
    nombre = REPR
    cls_ramas = [ProbRepr]
