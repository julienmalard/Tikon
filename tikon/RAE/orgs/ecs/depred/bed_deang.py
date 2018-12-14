import numpy as np

from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónDepred


class A(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class B(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class C(Parám):
    nombre = 'c'
    líms = (0, None)
    inter = ['presa', 'huésped']


class BedDeAng(EcuaciónDepred):
    """
    Depredación de respuesta funcional Beddington-DeAngelis. Incluye dependencia en el depredador.
    """
    nombre = 'Beddington-DeAngelis'
    cls_ramas = [A, B, C]

    def eval(símismo, paso):
        cf = símismo.cf

        dens_depred = dens[:, :, :, í_etps]  # La población de esta etapa
        depred_etp = np.multiply(dens, cf['a'] / (cf['b'] + dens + cf['c'] * dens_depred))

        return depred_etp
