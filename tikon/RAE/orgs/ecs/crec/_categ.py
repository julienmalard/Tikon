import numpy as np

from tikon.ecs.árb_mód import CategEc
from .ec import EcuaciónCrec
from .modif import ModifCrec


class EcsCrec(CategEc):
    nombre = 'Crecimiento'
    cls_ramas = [ModifCrec, EcuaciónCrec]
    _eje_cosos = 'etapa'
    _nombre_res = 'Crecimiento'

    def postproc(símismo, paso):

        crec = símismo.obt_res()
        pobs = símismo.obt_val_mód('Pobs')

        crec[np.isnan(crec)] = 0
        np.floor(crec)

        # Asegurarse que no perdimos más que existen
        np.maximum(-pobs, crec, out=crec)
        símismo.poner_val(crec)
        símismo.mód.poner_val('Pobs', crec, rel=True, índs=símismo.í_cosos)
