from tikon.ecs.árb_mód import Ecuación


class EcuaciónOrg(Ecuación):
    _eje_cosos = 'etapa'

    def pobs_etps(símismo, filtrar=True):
        return símismo.obt_val_mód('Pobs', filtrar=filtrar)

    def eval(símismo, paso):
        raise NotImplementedError
