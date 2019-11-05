from tikon.estruc.módulo import Módulo
from tikon.estruc.simul import SimulMódulo
from tikon.móds.clima.clima import Clima
from tikon.móds.cultivo.res import RES_BIOMASA
from tikon.móds.rae.orgs.plantas.externa import CultivoExterno
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.red.utils import RES_DEPR, EJE_VÍCTIMA, EJE_ETAPA, RES_POBS
from tikon.result.utils import EJE_PARC

from . import res


class Cultivo(Módulo):
    nombre = 'cultivo'

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        return SimulCultivo(simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)


class SimulCultivo(SimulMódulo):
    resultados = [res.ResBiomasa, res.ResHumedadSuelo]

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        símismo.simuls_parcelas = [prc.gen_simul() for prc in simul_exper.exper.parcelas]
        símismo.red = simul_exper[RedAE.nombre]
        símismo.clima = simul_exper[Clima.nombre]
        símismo.etapas = [etp for etp in símismo.red.etapas if isinstance(etp, CultivoExterno)]
        símismo.orgs = símismo.red.orgs
        símismo.superficies = simul_exper.exper.controles['superficies']

        super().__init__(mód=mód, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)

    def iniciar(símismo):
        for s in símismo.simuls_parcelas:
            s.iniciar()

    def incrementar(símismo, paso, f):
        símismo.aplicar_daño()
        for s in símismo.simuls_parcelas:
            s.incrementar(paso, f)
        símismo.mandar_biomasa()

    def aplicar_daño(símismo):
        depred = símismo.red.obt_valor(RES_DEPR)

        # Daño total (de todos herbívoros) por etapa de planta, por m2
        daño = depred.loc[{EJE_VÍCTIMA: símismo.etapas}].sum(dim=EJE_ETAPA) / símismo.superficies

        for prc in símismo:
            prc.aplicar_daño(daño.loc[{EJE_PARC: prc.parcelas}])

    def mandar_biomasa(símismo):
        símismo.red.poner_valor(RES_POBS, val=símismo.obt_valor(RES_BIOMASA) * símismo.superficies)

    def cerrar(símismo):
        for s in símismo.simuls_parcelas:
            s.cerrar()

    def requísitos(símismo, controles=False):
        return {req for prc in símismo for req in símismo[prc].requísitos(controles)}

    def __iter__(símismo):
        for prc in símismo.simuls_parcelas:
            yield prc
