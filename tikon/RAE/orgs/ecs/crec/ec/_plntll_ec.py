from tikon.ecs.árb_mód import Ecuación


class EcuaciónCrec(Ecuación):

    def crec_etps(símismo):
        return símismo.obt_res()

    def pobs_etps(símismo):
        return símismo.obt_val_mód('Pobs', índs=símismo._í_cosos)

    def __call__(símismo, paso):
        raise NotImplementedError
