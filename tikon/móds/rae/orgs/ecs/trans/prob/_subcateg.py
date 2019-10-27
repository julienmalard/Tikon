import numpy as np

from tikon.ecs.árb_mód import SubcategEc, EcuaciónVacía
from .cauchy import Cauchy
from .constante import Constante
from .gamma import Gamma
from .logística import Logística
from .normal import Normal


class ProbTrans(SubcategEc):
    nombre = 'Prob'
    cls_ramas = [Normal, EcuaciónVacía, Cauchy, Constante, Gamma, Logística]
    _nombre_res = TRANS
    _eje_cosos = EJE_ETAPA

    def postproc(símismo, paso):
        trans = símismo.obt_val_res(filtrar=False)

        # Redondear las transiciones calculadas
        np.floor(trans, out=trans)

        # Quitar los organismos que transicionaron
        símismo.poner_val_mód(POBS, -trans, rel=True, filtrar=True)
        símismo.poner_val_res(trans)

    def _imprimir(símismo):
        print(símismo.obt_val_mód(POBS, filtrar=False)[..., símismo.sim.cohortes.í_etps],
              np.sum(símismo.sim.cohortes._pobs, axis=0))
        print(símismo.obt_val_mód(POBS, filtrar=False)[..., símismo.sim.cohortes.í_etps] - np.sum(
            símismo.sim.cohortes._pobs, axis=0))
