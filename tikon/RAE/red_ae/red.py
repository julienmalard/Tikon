from tikon.RAE import Organismo
from tikon.módulo import Módulo
from tikon.rsltd.res import Resultado, Dims


class RedAE(Módulo):

    def __init__(símismo):
        super().__init__()

        símismo._orgs = {}

    def añadir_org(símismo, org):
        símismo._orgs[str(org)] = org

    def quitar_org(símismo, org):
        if isinstance(org, Organismo):
            org = str(org)
        try:
            símismo._orgs.pop(org)
        except KeyError:
            raise KeyError('El organismo {org} no existía en esta red.'.format(org=org))

    def iniciar(símismo, días, f_inic, paso, n_rep_estoc, n_rep_parám):

        super().iniciar()

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

    def n_etapas(símismo, fantasmas=False):
        pass

    def _calc_edad(símismo, paso):
        pass

    def _calc_depred(símismo, paso):
        pass

    def _calc_crec(símismo, paso):
        pass

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

    def _gen_resultados(símismo, í_pasos, n_rep_estoc, n_rep_parám, n_parc):

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

        obs = símismo._gen_obs()

        return {
            'Pobs': Resultado(dims_base, í_pasos, obs=obs['Pobs']),
            'Crec': Resultado(dims_base, í_pasos, obs=obs['Crec']),
            'Depred': Resultado(dims_inter, í_pasos, obs=obs['Depred']),
            'Reprod': Resultado(dims_base, í_pasos, obs=obs['Reprod']),
            'Muertes': Resultado(dims_base, í_pasos, obs=obs['Muertes']),
            'Trans': Resultado(dims_base, í_pasos, obs=obs['Trans']),
            'Mov': Resultado(dims_mov, í_pasos, obs=obs['Mov']),
            'Estoc': Resultado(dims_base, í_pasos, obs=obs['Estoc'])
        }

    def _gen_obs(símismo):
        pass
