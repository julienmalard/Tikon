from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.rae.orgs.ecs.utils import probs_conj
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.utils import RES_POBS
from tikon.móds.trampa.ecs.utils import ECS_CAPTURA
from tikon.móds.trampa.utils import EJE_TRAMPA, RES_CAPTURA, RES_DENS

from .sec_hiper import SecanteHiperbólica


class EcCaptura(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [SecanteHiperbólica, EcuaciónVacía]
    _nombre_res = RES_CAPTURA
    eje_cosos = EJE_TRAMPA


class EcsCaptura(CategEc):
    nombre = ECS_CAPTURA
    cls_ramas = [EcCaptura]
    _nombre_res = RES_CAPTURA
    eje_cosos = EJE_TRAMPA

    def postproc(símismo, paso, sim):
        prob_captura = símismo.obt_valor_res(sim)
        dens = símismo.obt_valor_mód(sim, RES_DENS)
        prob_escape = 1 - prob_captura
        prob_captura_final = probs_conj(1 - prob_escape ** dens ** paso, dim=EJE_TRAMPA)
        símismo.poner_valor_res(sim, prob_captura_final)

        prob_captura_final = prob_captura_final.sum(dim=EJE_TRAMPA)
        pobs = símismo.obt_valor_extern(sim, RES_POBS, mód=RedAE.nombre)
        símismo.poner_valor_extern(sim, var=RES_POBS, mód=RedAE.nombre, val=pobs * prob_captura_final)
