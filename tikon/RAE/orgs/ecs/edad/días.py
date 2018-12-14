from .._plntll_ec import EcuaciónOrg


class FuncDías(EcuaciónOrg):
    """
    Edad por día.
    """
    nombre = 'Días'

    def eval(self, paso):
        return paso
