from tikon.móds.cultivo.extrn import ParcelasCultivoExterno, SimulCultivoExterno, InstanciaSimulCultivo
from tikon.móds.cultivo.res import RES_HUMSUELO, RES_BIOMASA
from tikon.utils import EJE_ESTOC, EJE_PARÁMS


class MiInstanciaSimulCultivo(InstanciaSimulCultivo):

    def __init__(símismo, sim, índs, reps):
        símismo.biomasa = sim.parcelas.biomasa
        símismo.hum_suelo = sim.parcelas.hum_suelo
        super().__init__(sim=sim, índs=índs, reps=reps)

    def incrementar(símismo, paso, f):
        pass

    def llenar_vals(símismo):
        símismo.datos[RES_BIOMASA][:] = símismo.biomasa
        símismo.datos[RES_HUMSUELO][:] = símismo.hum_suelo

    def aplicar_daño(símismo, daño):
        pass

    def cerrar(símismo):
        pass


class MiSimulCultivoExterno(SimulCultivoExterno):
    cls_instancia = MiInstanciaSimulCultivo

    def requísitos(símismo, controles=False):
        pass


class MiParcelaCultivoExterno(ParcelasCultivoExterno):

    def __init__(símismo, parcelas, hum_suelo, biomasa, combin=(EJE_ESTOC, EJE_PARÁMS)):
        símismo.hum_suelo = hum_suelo
        símismo.biomasa = biomasa
        super().__init__(parcelas, combin)

    def gen_simul(símismo, sim):
        return MiSimulCultivoExterno(sim, parcelas=símismo)
