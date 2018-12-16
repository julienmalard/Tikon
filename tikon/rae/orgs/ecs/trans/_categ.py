import numpy as np

from tikon.ecs.árb_mód import CategEc
from .mult import MultTrans
from .prob import ProbTrans


class EcsTrans(CategEc):
    nombre = 'Transiciones'
    cls_ramas = [ProbTrans, MultTrans]
    _nombre_res = 'Reproducción'
    _eje_cosos = 'etapa'

    def postproc(símismo, paso):
        trans = símismo.mód.obt_res('Transiciones')

        # Si no eran adultos muríendose por viejez, añadirlos a la próxima etapa también
        res_pobs = símismo.mód.obt_res('Pobs')
        trans_de, trans_a = zip(*símismo.mód.í_trans())

        # para hacer: limpiar
        í_trans_de = [símismo.í_cosos.index(í) for í in trans_de]

        res_pobs.poner_valor(
            trans, rel=True, índs={símismo._eje_cosos: símismo.mód.í_trans()}
        )  # para hacer: emplear mód.agregar_pobs(), con servicio de cohortes incluído.

        nuevos = np.zeros_like(trans)

        for i in range(len(símismo.etapas)):
            i_recip = orden_recip[i]
            if i_recip != -1:
                nuevos[..., i_recip] += trans[..., i]

        np.add(pobs, nuevos, out=pobs)

        if len(símismo.índices_cohortes):
            símismo._añadir_a_cohortes(nuevos=nuevos[..., símismo.índices_cohortes])
