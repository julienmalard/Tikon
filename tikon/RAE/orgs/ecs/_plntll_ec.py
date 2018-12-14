from tikon.ecs.árb_mód import Ecuación


class EcuaciónOrg(Ecuación):
    _eje_cosos = 'etapa'

    def eval(símismo, paso):
        raise NotImplementedError
