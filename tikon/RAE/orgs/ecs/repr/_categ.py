from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from .cauchy import Cauchy
from .constante import Constante
from .depred import Depred
from .gamma import Gamma
from .logística import Logística
from .normal import Normal
from .t import T
from .triang import Triang


class ProbRepr(SubcategEc):
    nombre = 'Prob'
    cls_ramas = [EcuaciónVacía, Constante, Depred, Normal, Triang, Cauchy, Gamma, Logística, T]
    auto = Constante
    _nombre_res = 'Reproducción'
    _eje_cosos = 'etapa'

    def postproc(símismo, paso):
        # Agregar las reproducciones a las poblaciones
        reprod = símismo.obt_res(filtrar=False)

        res_pobs = símismo.mód.obt_res('Pobs')
        res_pobs.poner_valor(
            reprod, rel=True, índs={símismo._eje_cosos: símismo.mód.í_repr()}
        )  # para hacer: emplear mód.agregar_pobs(), con servicio de cohortes incluído.


class EcsRepr(CategEc):
    nombre = 'Reproducción'
    cls_ramas = [ProbRepr]
