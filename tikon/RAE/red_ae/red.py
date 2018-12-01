from tikon.módulo import Módulo
from tikon.rsltd.res import Resultado, Dims
from .mnjdr_ecs import EcsSimul
from .. import Organismo


class RedAE(Módulo):

    def __init__(símismo):
        super().__init__()

        símismo._orgs = {}
        símismo._etps = []
        símismo._ecs_simul = None  # type: EcsSimul

    def añadir_org(símismo, org):
        símismo._orgs[str(org)] = org

    def quitar_org(símismo, org):
        if isinstance(org, Organismo):
            org = str(org)
        try:
            símismo._orgs.pop(org)
        except KeyError:
            raise KeyError('El organismo {org} no existía en esta red.'.format(org=org))

    def etapas(símismo, fantasmas=False):
        return [etp for org in símismo._orgs for etp in org.etapas(fantasmas=fantasmas)]

    def iniciar_estruc(símismo, tiempo, conex_móds, calibs, n_rep_estoc, n_rep_parám):
        símismo._etps = símismo.etapas(fantasmas=True)
        símismo._ecs_simul = EcsSimul(símismo._etps, calibs, n_rep_parám)

        super().iniciar_estruc(tiempo, conex_móds, calibs, n_rep_estoc, n_rep_parám)

    def incrementar(símismo, paso):

        símismo._calc_edad(paso)
        símismo._calc_depred(paso)
        símismo._calc_crec(paso)
        símismo._calc_reprod(paso)
        símismo._calc_muertes(paso)
        símismo._calc_trans(paso)
        símismo._calc_mov(paso)
        símismo._calc_estoc(paso)

    def cerrar(símismo):
        pass

    def _calc_edad(símismo, paso):
        for ec_edad, etps in símismo._ecs_simul['Edad']['Ecuación']:
            ec_edad.evaluar(etps, paso, símismo)

    def _calc_depred(símismo, paso):
        for ec_depred, etps in símismo._ecs_simul['Depredación']['Ecuación']:
            ec_depred.evaluar(etps, paso, símismo)

    def _calc_crec(símismo, paso):
        for modif_crec, etps in símismo._ecs_simul['Crecimiento']['Modif']:
            modif_crec.evaluar(etps, paso, símismo)

        for ec_crec, etps in símismo._ecs_simul['Crecimiento']['Ecuación']:
            ec_crec.evaluar(etps, paso, símismo)

    def _calc_reprod(símismo, paso):
        pass

    def _calc_muertes(símismo, paso):
        pass

    def _calc_trans(símismo, paso):
        pass

    def _calc_mov(símismo, paso):
        pass

    def _calc_estoc(símismo, paso):
        pass

    def _gen_resultados(símismo, n_rep_estoc, n_rep_parám, n_parc):

        n_etps = símismo.n_etapas(fantasmas=True)
        dims_base = Dims(
            n_estoc=n_rep_estoc, n_parám=n_rep_parám, n_parc=n_parc, coords={'etapa': n_etps}
        )
        dims_inter = Dims(
            n_estoc=n_rep_estoc, n_parám=n_rep_parám, n_parc=n_parc, coords={'etapa': n_etps, 'víctima': n_etps}
        )
        dims_mov = Dims(
            n_estoc=n_rep_estoc, n_parám=n_rep_parám, n_parc=n_parc, coords={'etapa': n_etps, 'dest': n_parc}
        )

        n_pasos = símismo.tiempo.n_pasos()

        return {
            'Pobs': Resultado(dims_base),
            'Crec': Resultado(dims_base),
            'Depred': Resultado(dims_inter),
            'Reprod': Resultado(dims_base),
            'Muertes': Resultado(dims_base),
            'Trans': Resultado(dims_base),
            'Mov': Resultado(dims_mov),
            'Estoc': Resultado(dims_base),
        }

    def __getitem__(símismo, itema):
        return símismo._orgs[str(itema)]

    def __iter__(símismo):
        for org in símismo._orgs.values():
            yield org
