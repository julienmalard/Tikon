from tikon.estruc.módulo import Módulo
from tikon.estruc.simul import SimulMódulo
from tikon.móds.apli.res import ResConcentración, ResDecomp, ResMortalidad


class Aplicaciones(Módulo):
    nombre = 'aplicaciones'

    def __init__(símismo, productos):
        super().__init__(productos)

    @property
    def productos(símismo):
        return [símismo[prod] for prod in símismo]

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        return SimulAplicaciones(mód=símismo, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)


class SimulAplicaciones(SimulMódulo):
    resultados = [ResDecomp, ResConcentración, ResMortalidad]

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        super().__init__(mód, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)

    def requísitos(símismo, controles=False):
        pass
