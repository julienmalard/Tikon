import numpy as np
from tikon.móds.rae.orgs.ecs._plntll import CategEcOrg
from tikon.móds.rae.orgs.ecs.utils import ECS_TRANS
from tikon.móds.rae.utils import EJE_ETAPA, RES_TRANS

from .deter import TransDeter
from .mult import MultTrans
from .prob import TransProb


class EcsTrans(CategEcOrg):
    nombre = ECS_TRANS
    cls_ramas = [TransProb, TransDeter, MultTrans]
    _nombre_res = RES_TRANS

    def postproc(símismo, paso, sim):
        trans = símismo.obt_valor_res(sim)  # Redondear las transiciones calculadas
        trans.values[:] = np.floor(trans.values)

        # Si no eran adultos muríendose por viejez, añadirlos a la próxima etapa también
        trans_de, trans_a = zip(*sim.recip_trans)

        trans = trans[{EJE_ETAPA: list(trans_de)}]
        trans[EJE_ETAPA] = list(trans_a)

        símismo.ajust_pobs(sim, trans)
