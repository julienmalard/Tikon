from .._plntll import EcuaciónOrg


class FuncDías(EcuaciónOrg):
    """
    Edad por día.
    """
    nombre = 'Días'

    def eval(símismo, paso, sim):
        return paso
