from ._plntll_ec import EcuaciónCrec


class Expon(EcuaciónCrec):
    """
    Crecimiento exponencial
    """

    nombre = 'Exponencial'

    # El exponencial no tiene parámetros a parte de r

    def eval(símismo, paso, sim):
        return símismo.obt_val_res(sim) * símismo.pobs(sim)
