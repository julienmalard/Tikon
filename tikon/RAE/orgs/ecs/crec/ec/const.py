from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónCrec


class N(Parám):
    nombre = 'n'
    líms = (0, None)


class Constante(EcuaciónCrec):
    """
    Población constante para toda la simulación. Útil para pruebas.
    """

    nombre = 'Constante'
    _cls_ramas = [N]

    def __call__(símismo, paso):
        nueva_pob = símismo.cf['n']
        return nueva_pob - símismo.pobs_etps()
