from ._plntll_ec import EcuaciónCrec


class Expon(EcuaciónCrec):
    """
    Crecimiento exponencial
    """

    nombre = 'Exponencial'
    # El exponencial no tiene parámetros a parte de r

    def __call__(símismo, paso):
        return símismo.crec_etps() * símismo.pobs_etps()
