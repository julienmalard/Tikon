from .._plntll_ec import EcuaciónOrg


class EcuaciónMuertes(EcuaciónOrg):
    _nombre_res = 'Muertes'

    def eval(símismo, paso):
        raise NotImplementedError
