import numpy as np

from tikon.ecs.árb_mód import CategEc
from .ec import EcuaciónCrec
from .modif import ModifCrec


class EcsCrec(CategEc):
    nombre = 'Crecimiento'
    cls_ramas = [ModifCrec, EcuaciónCrec]
    _eje_cosos = 'etapa'
    _nombre_res = 'Crecimiento'
    req_todas_ramas = True

    def postproc(símismo, paso):

        crec = símismo.obt_res(filtrar=False)  # para hacer: filtara=False debería ser automático para CategEc
        pobs = símismo.obt_val_mód('Pobs')

        # Evitar pérdidas de poblaciones superiores a la población.
        crec[np.isnan(crec)] = -pobs[np.isnan(crec)]

        símismo.poner_val_res(crec)
        símismo.poner_val_mód('Pobs', crec, rel=True)
