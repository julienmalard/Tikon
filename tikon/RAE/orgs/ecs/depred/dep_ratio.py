import numpy as np

from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónDepred


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class TipoIDR(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo I con dependencia en el ratio de presa a depredador.
    """

    nombre = 'Tipo I_Dependiente ratio'
    cls_ramas = [ATipoI]

    def eval(símismo, paso):
        dens = símismo.obt_val_mód('Dens')
        return np.multiply(dens / símismo.dens_depred(), símismo.cf['a'])


class ATipoII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class BTipoII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIDR(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo II con dependencia en el ratio de presa a depredador.
    """
    nombre = 'Tipo II_Dependiente ratio'
    cls_ramas = [ATipoII, BTipoII]

    def eval(símismo, paso):
        cf = símismo.cf
        dens_depred = símismo.dens_depred()
        return np.multiply(dens / dens_depred, cf['a'] / (dens / dens_depred + cf['b']))


class ATipoIII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class BTipoIII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIIDR(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo III con dependencia en el ratio de presa a depredador.
    """
    nombre = 'Tipo III_Dependiente ratio'
    cls_ramas = [ATipoIII, BTipoIII]

    def eval(símismo, paso):
        dens_depred = símismo.dens_depred()
        cf = símismo.cf

        return np.multiply(np.square(dens / dens_depred), cf['a'] / (np.square(dens / dens_depred) + cf['b']))
