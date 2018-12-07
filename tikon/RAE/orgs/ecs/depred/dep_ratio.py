import numpy as np

from tikon.ecs.árb_mód import Ecuación, Parám


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class TipoIDR(Ecuación):
    """
    Depredación de respuesta funcional tipo I con dependencia en el ratio de presa a depredador.
    """

    nombre = 'Tipo I_Dependiente ratio'
    _cls_ramas = [ATipoI]

    def __call__(símismo, paso):
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


class TipoIIDR(Ecuación):
    """
    Depredación de respuesta funcional tipo II con dependencia en el ratio de presa a depredador.
    """
    nombre = 'Tipo II_Dependiente ratio'
    _cls_ramas = [ATipoII, BTipoII]

    def __call__(símismo, paso):
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


class TipoIIIDR(Ecuación):
    """
    Depredación de respuesta funcional tipo III con dependencia en el ratio de presa a depredador.
    """
    nombre = 'Tipo III_Dependiente ratio'
    _cls_ramas = [ATipoIII, BTipoIII]

    def __call__(símismo, paso):
        dens_depred = símismo.dens_depred()
        cf = símismo.cf

        return np.multiply(np.square(dens / dens_depred), cf['a'] / (np.square(dens / dens_depred) + cf['b']))
