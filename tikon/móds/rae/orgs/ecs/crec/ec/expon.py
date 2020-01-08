from ._plntll_ec import EcuaciónCrec


class Expon(EcuaciónCrec):
    """
    Crecimiento exponencial
    """

    nombre = 'Exponencial'

    # El exponencial no tiene parámetros además de r

    def eval(símismo, paso, sim):
        r = símismo.obt_valor_res(sim)
        return r * símismo.pobs(sim)
