import numpy as np

from tikon.ecs.árb_mód import CategEc
from .ec import EcuaciónCrec
from .modif import ModifCrec


class EcsCrec(CategEc):
    nombre = 'Crecimiento'
    _cls_ramas = [ModifCrec, EcuaciónCrec]

    def __call__(símismo, paso):
        crec = símismo.obt_res()
        pobs = símismo.obt_val_mód('Pobs', símismo._í_cosos)

        crec[np.isnan(crec)] = 0
        np.floor(crec)

        # Asegurarse que no perdimos más que existen
        np.maximum(-pobs, crec, out=crec)
        símismo.poner_val(crec)
        símismo.mód.poner_val('Pobs', crec, rel=True, índs=símismo._í_cosos)
