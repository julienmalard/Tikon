from .._plntll_ec import EcuaciónOrg


class EcuaciónMuertes(EcuaciónOrg):
    _nombre_res = MRTE

    def eval(símismo, paso, sim):
        raise NotImplementedError
