import numpy as np

from tikon.ecs.árb_mód import SubcategEc, EcuaciónVacía
from .cauchy import Cauchy
from .constante import Constante
from .gamma import Gamma
from .logística import Logística
from .normal import Normal


class ProbTrans(SubcategEc):
    nombre = 'Prob'
    cls_ramas = [EcuaciónVacía, Cauchy, Constante, Gamma, Logística, Normal]
    auto = Normal
    _nombre_res = 'Transiciones'
    _eje_cosos = 'etapa'

    def postproc(símismo, paso):
        trans = símismo.obt_res(filtrar=False)

        # Redondear las transiciones calculadas
        np.floor(trans, out=trans)

        # Quitar los organismos que transicionaron
        símismo.poner_val_mód('Pobs', -trans, rel=True, filtrar=True)
        símismo.poner_val_res(trans)

    def _imprimir(símismo):
        print(símismo.obt_val_mód('Pobs', filtrar=False)[..., símismo.mód.cohortes.í_etps],
              np.sum(símismo.mód.cohortes._pobs, axis=0))
        print(símismo.obt_val_mód('Pobs', filtrar=False)[..., símismo.mód.cohortes.í_etps] - np.sum(
            símismo.mód.cohortes._pobs, axis=0))
