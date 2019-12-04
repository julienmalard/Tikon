from ._plntll_ec import EcuaciónEdad


class FuncDías(EcuaciónEdad):
    """
    Edad por día.
    """
    nombre = 'Días'

    def eval(símismo, paso, sim):
        return paso
