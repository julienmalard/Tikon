from tikon.ecs.árb_mód import CategEc
from .mult import MultTrans
from .prob import ProbTrans


class EcsTrans(CategEc):
    nombre = 'Transiciones'
    cls_ramas = [ProbTrans, MultTrans]
    _nombre_res = 'Reproducción'
    _eje_cosos = 'etapa'

    def postproc(símismo, paso):
        # Si no eran adultos muríendose por viejez, añadirlos a la próxima etapa también
        trans_de, trans_a = zip(*símismo.mód.etps_trans())

        # para hacer: limpiar
        trans = símismo.mód.obt_res('Transiciones').obt_valor(índs={símismo._eje_cosos: trans_de})

        símismo.mód.agregar_pobs(trans, etapas=trans_a)
