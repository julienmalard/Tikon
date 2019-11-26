from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.apli.ecs.utils import ECS_MRTLD
from tikon.móds.apli.utils import EJE_PRODUCTO, RES_MRTLD
from tikon.móds.rae.orgs.ecs.utils import probs_conj
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.utils import RES_POBS

from .logíst import Logística


class EcMortalidad(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [Logística, EcuaciónVacía]
    _nombre_res = RES_MRTLD
    eje_cosos = EJE_PRODUCTO


class EcsMortalidad(CategEc):
    nombre = ECS_MRTLD
    cls_ramas = [EcMortalidad]
    _nombre_res = RES_MRTLD
    eje_cosos = EJE_PRODUCTO

    def postproc(símismo, paso, sim):
        mortalidad = símismo.obt_valor_res(sim)
        sobrevivencia = 1 - mortalidad
        mortalidad = 1 - sobrevivencia ** paso
        mortalidad = probs_conj(mortalidad, dim=EJE_PRODUCTO)
        símismo.poner_valor_res(sim, mortalidad)

        mortalidad = mortalidad.sum(dim=EJE_PRODUCTO)
        pobs = símismo.obt_valor_extern(sim, RES_POBS, mód=RedAE.nombre)
        símismo.poner_valor_extern(sim, var=RES_POBS, mód=RedAE.nombre, val=pobs * mortalidad)
