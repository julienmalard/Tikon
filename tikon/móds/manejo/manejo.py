from copy import deepcopy

from tikon.central.módulo import Módulo
from tikon.central.simul import SimulMódulo
from tikon.datos.datos import Datos
from tikon.móds.manejo.acciones import Acción


class Regla(object):
    def __init__(símismo, condición, acción):
        símismo.condición = deepcopy(condición)
        símismo.acción = [acción] if isinstance(acción, Acción) else acción

    def requísitos(símismo, controles):
        reqs_cond = símismo.condición.requísitos(controles) or {}
        reqs_acción = {req for a in símismo.acción for req in (a.requísitos(controles) or {})}
        return reqs_acción.union(reqs_cond)

    def __call__(símismo, sim, paso, f):
        cond_verdad = símismo.condición(sim, paso, f)
        if cond_verdad.qualquier() if isinstance(cond_verdad, Datos) else cond_verdad:
            for a in símismo.acción:
                a(sim, donde=cond_verdad)


class SimulManejo(SimulMódulo):

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        símismo.reglas = mód.reglas
        super().__init__(mód, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)

    def requísitos(símismo, controles=False):
        return {req for rgl in símismo.reglas for req in rgl.requísitos(controles)}

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        for r in símismo.reglas:
            r(sim=símismo.simul_exper, paso=paso, f=f)


class Manejo(Módulo):
    nombre = 'manejo'
    cls_simul = SimulManejo

    def __init__(símismo, reglas=None):
        if isinstance(reglas, Regla):
            reglas = [reglas]
        símismo.reglas = reglas or []

        super().__init__()
