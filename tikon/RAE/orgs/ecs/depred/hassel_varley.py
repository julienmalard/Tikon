import numpy as np

from tikon.ecs.árb_mód import Ecuación, Parám


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']


class MTipoI(Parám):
    nombre = 'm'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIHasselVarley(Ecuación):
    """
    Depredación de respuesta funcional Tipo I con dependencia Hassell-Varley.
    """
    nombre = 'Tipo I_Hassell-Varley'
    _cls_ramas = [ATipoI, MTipoI]

    def __call__(símismo, paso):
        dens_depred = símismo.dens_depred()
        cf = símismo.cf
        return np.multiply(dens / dens_depred ** cf['m'], cf['a'])


class ATipoII(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']


class BTipoII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class MTipoII(Parám):
    nombre = 'm'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIHasselVarley(Ecuación):
    """
    Depredación de respuesta funcional Tipo II con dependencia Hassell-Varley.
    """

    nombre = 'Tipo I_Hassell-Varley'
    _cls_ramas = [ATipoII, BTipoII, MTipoII]

    def __call__(símismo, paso):
        dens_depred = símismo.dens_depred()
        cf = símismo.cf
        return np.multiply(dens / dens_depred ** cf['m'], cf['a'] / (dens / dens_depred ** cf['m'] + cf['b']))


class ATipoIII(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']


class BTipoIII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class MTipoIII(Parám):
    nombre = 'm'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIIHasselVarley(Ecuación):
    """
    Depredación de respuesta funcional Tipo III con dependencia Hassell-Varley.
    """

    nombre = 'Tipo I_Hassell-Varley'
    _cls_ramas = [ATipoIII, BTipoIII, MTipoIII]

    def __call__(símismo, paso):
        dens_depred = símismo.dens_depred()
        cf = símismo.cf
        return np.multiply(dens / dens_depred ** cf['m'], cf['a'] / (dens / dens_depred ** cf['m'] + cf['b']))

