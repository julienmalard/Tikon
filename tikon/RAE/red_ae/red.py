from tikon.módulo import Módulo
from tikon.rsltd.res import Resultado, Dims
from .mnjdr_ecs import MnjdrEcsRed
from .. import Organismo


class RedAE(Módulo):

    def __init__(símismo):
        super().__init__()

        símismo._orgs = {}
        símismo._etps = []
        símismo._ecs_simul = None  # type: MnjdrEcsRed

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

    def paráms(símismo):
        return [pr for etp in símismo for pr in etp.paráms()]

    def iniciar_estruc(símismo, tiempo, conex_móds, calibs, n_rep_estoc, n_rep_parám):
        símismo._etps = símismo.etapas(fantasmas=True)
        símismo._ecs_simul = MnjdrEcsRed(símismo._etps, calibs, n_rep_parám)

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

    def poner_valor(símismo, var, valor, rel=False):
        if var =='Poblaciones':
            símismo
        else:
            raise ValueError

    def agregar_pobs(símismo):
        pass

    def quitar_pobs(símismo):
        pass

    def ajustar_pobs(símismo):
        pass

    def _calc_edad(símismo, paso):
        símismo._ecs_simul['Edad'].evaluar(paso)

    def _calc_depred(símismo, paso):
        símismo._ecs_simul['Depredación'].evaluar(paso)

    def _calc_crec(símismo, paso):
        crec = símismo._ecs_simul['Crecimiento']
        crec.evaluar(paso)
        símismo.agregar_pobs(símismo.resultados['Crecimiento'])

    def _calc_reprod(símismo, paso):
        símismo._ecs_simul['Reproducción'].evaluar(paso)
        símismo.agregar_pobs(símismo.resultados['Reproducción'])

    def _calc_muertes(símismo, paso):
        símismo._ecs_simul['Muertes'].evaluar(paso)
        símismo.quitar_pobs(símismo.resultados['Muertes'])  #para hacer: índices

    def _calc_trans(símismo, paso):
        símismo._ecs_simul['Transiciones'].evaluar(paso)

    def _calc_mov(símismo, paso):
        símismo._ecs_simul['Movimiento'].evaluar(paso)

    def _calc_estoc(símismo, paso):
        símismo._ecs_simul['Estoc'].evaluar(paso)

    def _coords_resultados(símismo):

        l_res = ['Crecimiento', 'Reproducción', 'Muertes', 'Transiciones', 'Estoc']
        parc = símismo.obt_val_manejo('parcelas')
        return {
            'Pobs': {'etapa': símismo._etps},
            'Depredación': {'etapa': símismo._ecs_simul.etapas_categ('Depredación'), 'víctima': símismo._etps},
            'Movimiento': {'etapa': símismo._ecs_simul.etapas_categ('Movimiento'), 'dest': parc},
            **{res: {'etapa': símismo._ecs_simul.etapas_categ(res)} for res in l_res}
        }

    def __getitem__(símismo, itema):
        return símismo._orgs[str(itema)]

    def __iter__(símismo):
        for org in símismo._orgs.values():
            yield org
