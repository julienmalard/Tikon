import numpy as np

from tikon.ecs.árb_mód import Ecuación, Parám


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class TipoIDP(Ecuación):
    """
    Depredación de respuesta funcional tipo I con dependencia en la población de la presa.
    """

    nombre = 'Tipo I_Dependiente presa'
    cls_ramas = [ATipoI]

    def eval(símismo, paso):
        return np.multiply(pobs, símismo.cf['a'])


class ATipoII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class BTipoII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIDP(Ecuación):
    """
    Depredación de respuesta funcional tipo II con dependencia en la población de la presa.
    """

    nombre = 'Tipo I_Dependiente presa'
    cls_ramas = [ATipoII]

    def eval(símismo, paso):
        cf = símismo.cf
        dens = símismo.obt_val_mód('Dens')
        return np.multiply(dens, cf['a'] / (dens + cf['b']))


class ATipoIII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class BTipoIII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIIDP(Ecuación):
    """
    Depredación de respuesta funcional tipo III con dependencia en la población de la presa.
    """

    nombre = 'Tipo III_Dependiente presa'
    cls_ramas = [ATipoIII, BTipoIII]

    def eval(símismo, paso):
        cf = símismo.cf
        dens = símismo.obt_val_mód('Dens')
        return np.multiply(np.square(dens), cf['a'] / (np.square(dens) + cf['b']))
