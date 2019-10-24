from tikon.ecs.árb_mód import Ecuación


class EcuaciónOrg(Ecuación):
    _eje_cosos = EJE_ETAPA

    def pobs_etps(símismo, filtrar=True):
        return símismo.obt_val_mód(POBS, filtrar=filtrar)

    def eval(símismo, paso, sim):
        raise NotImplementedError
