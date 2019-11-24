import numpy as np
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg


class A(Parám):
    nombre = 'a'
    líms = (None, None)
    unids = 'C'


class B(Parám):
    nombre = 'b'
    líms = (0, None)
    unids = 'C'


class SigmoidalTemperatura(EcuaciónOrg):
    """
    Sobrevivencia que disminuye con temperatura creciente según relación sigmoidal.
    """

    nombre = 'Sigmoidal Temperatura'
    cls_ramas = [A, B]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        temp_máx = símismo.obt_valor_extern(sim, 'clima.temp_máx')
        sobrevivencia = 1 / (1 + np.exp((temp_máx - cf['a']) / cf['b']))
        return 1 - sobrevivencia

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_máx'}
