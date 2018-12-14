from ..._plntll_ec import EcuaciónOrg


class EcuaciónCrec(EcuaciónOrg):
    _nombre_res = 'Crecimiento'

    def crec_etps(símismo):
        return símismo.obt_res()

    def pobs_etps(símismo):
        return símismo.obt_val_mód('Pobs')

    def eval(símismo, paso):
        raise NotImplementedError
