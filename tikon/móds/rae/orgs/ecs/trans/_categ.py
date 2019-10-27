from tikon.móds.rae.orgs.ecs._plntll import CategEcOrg
from tikon.móds.rae.red.utils import EJE_ETAPA, RES_TRANS

from .mult import MultTrans
from .prob import ProbTrans


class EcsTrans(CategEcOrg):
    nombre = 'Transiciones'
    cls_ramas = [ProbTrans, MultTrans]
    _nombre_res = RES_TRANS

    def postproc(símismo, paso, sim):
        # Si no eran adultos muríendose por viejez, añadirlos a la próxima etapa también
        trans_de, trans_a = zip(*sim.etps_trans)

        trans = sim.obt_val_res(sim).loc[{EJE_ETAPA: trans_de}]
        trans[EJE_ETAPA] = trans_a

        símismo.ajust_pobs(sim, trans)
