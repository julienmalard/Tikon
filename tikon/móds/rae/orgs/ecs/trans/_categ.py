from tikon.ecs.árb_mód import CategEc
from tikon.móds.rae.orgs.utils import REPR, EDAD, POBS

from .mult import MultTrans
from .prob import ProbTrans


class EcsTrans(CategEc):
    nombre = 'Transiciones'
    cls_ramas = [ProbTrans, MultTrans]
    _nombre_res = REPR
    _eje_cosos = ETAPA

    def postproc(símismo, paso):
        # Si no eran adultos muríendose por viejez, añadirlos a la próxima etapa también
        trans_de, trans_a = zip(*símismo.sim.etps_trans())

        # para hacer: limpiar
        trans = símismo.sim.obt_res(TRANS).obt_valor(índs={símismo._eje_cosos: trans_de})

        símismo.sim.agregar_pobs(trans, etapas=trans_a)
