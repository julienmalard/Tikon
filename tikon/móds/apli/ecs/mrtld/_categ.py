from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.apli.ecs.utils import ECS_MRTLD
from tikon.móds.apli.utils import EJE_PRODUCTO, RES_MRTLD
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.utils import RES_POBS

from .logíst import Logística


class EcuaciónMortalidad(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [Logística, EcuaciónVacía]
    _nombre_res = RES_MRTLD
    eje_cosos = EJE_PRODUCTO

    def postproc(símismo, paso, sim):
        mortalidad = símismo.obt_valor_res(sim)
        sobrevivencia = 1 - mortalidad
        mortalidad_final = 1 - sobrevivencia ** paso
        símismo.poner_valor_res(sim, mortalidad_final)


class EcsMortalidad(CategEc):
    nombre = ECS_MRTLD
    cls_ramas = [EcuaciónMortalidad]

    def postproc(símismo, paso, sim):
        mortalidad = símismo.obt_valor_res(sim)
        pobs = símismo.obt_valor_extern(sim, RES_POBS, mód=RedAE.nombre)
        símismo.poner_valor_extern(sim, var=RES_POBS, val=pobs * mortalidad)
