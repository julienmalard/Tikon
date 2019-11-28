from tikon.central.errores import ErrorRequísitos
from tikon.central.módulo import Módulo
from tikon.central.simul import SimulMódulo
from tikon.móds.clima import Clima
from tikon.móds.cultivo.res import RES_BIOMASA
from tikon.móds.rae.orgs.plantas.externa import CultivoExterno
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.utils import RES_DEPR, EJE_VÍCTIMA, EJE_ETAPA, RES_POBS
from tikon.utils import EJE_PARC

from . import res


class SimulCultivo(SimulMódulo):
    resultados = [res.ResBiomasa, res.ResHumedadSuelo]

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):

        if RedAE.nombre not in simul_exper.modelo:
            raise ErrorRequísitos('Falta módulo RedAE requerido por Cultivo.')

        símismo.mód_red = simul_exper.modelo[RedAE.nombre]
        símismo.orgs = [org for org in símismo.mód_red.orgs if isinstance(org, CultivoExterno)]
        símismo.etapas = [etp for org in símismo.orgs for etp in org]

        super().__init__(mód=mód, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)

        símismo.simuls_parcelas = [prc.gen_simul(símismo) for prc in simul_exper.exper.grupos_parc]
        símismo.superficies = símismo.exper.controles['superficies']

    @property
    def red(símismo):
        return símismo.simul_exper[RedAE.nombre]

    @property
    def clima(símismo):
        if Clima.nombre in símismo.simul_exper:
            return símismo.simul_exper[Clima.nombre]

    def iniciar(símismo):
        super().iniciar()
        for s in símismo.simuls_parcelas:
            s.iniciar()
        símismo.mandar_biomasa()

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)

        símismo.aplicar_daño()
        for s in símismo.simuls_parcelas:
            s.incrementar(paso, f)
        símismo.mandar_biomasa()

    def aplicar_daño(símismo):
        depred = símismo.red.obt_valor(RES_DEPR)

        # Daño total (de todos herbívoros) por etapa de planta, por m2
        daño = depred.loc[{EJE_VÍCTIMA: símismo.etapas}].sum(dim=EJE_ETAPA) / símismo.superficies

        for prc in símismo.simuls_parcelas:
            prc.aplicar_daño(daño.loc[{EJE_PARC: [str(p) for p in prc.parcelas]}])

    def mandar_biomasa(símismo):
        símismo.red.poner_valor(RES_POBS, val=símismo.obt_valor(RES_BIOMASA) * símismo.superficies)

    def cerrar(símismo):
        for s in símismo.simuls_parcelas:
            s.cerrar()
        super().cerrar()

    def requísitos(símismo, controles=False):
        reqs_externos = {req for prc in símismo.simuls_parcelas for req in prc.requísitos(controles) or {}}
        req_adicional = {'superficies'} if controles else {'{red}.{depred}'.format(red=RedAE.nombre, depred=RES_DEPR)}
        return reqs_externos.union(req_adicional)


class Cultivo(Módulo):
    nombre = 'cultivo'
    cls_simul = SimulCultivo

    def __init__(símismo):
        super().__init__(cosos=None)
