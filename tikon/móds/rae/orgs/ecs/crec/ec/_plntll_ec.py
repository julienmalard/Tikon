from ..._plntll_ec import EcuaciónOrg


class EcuaciónCrec(EcuaciónOrg):
    _nombre_res = CREC

    def crec_etps(símismo):
        return símismo.obt_res()

    def eval(símismo, paso):
        raise NotImplementedError
