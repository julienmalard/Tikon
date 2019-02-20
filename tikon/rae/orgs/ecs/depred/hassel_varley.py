import numpy as np

from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónDepred


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']


class MTipoI(Parám):
    nombre = 'm'
    líms = (0, None)
    unids = None
    inter = ['presa', 'huésped']


class TipoIHasselVarley(EcuaciónDepred):
    """
    Depredación de respuesta funcional Tipo I con dependencia Hassell-Varley.

    M.P. Hassell, G.C. Varley. New inductive population model for insect parasites and its bearing on
        biological control. Nature, 223 (1969), pp. 1133–1136

    P en las respuestas funcionales de  cambia a P/(D^m)

    """
    nombre = 'Tipo I_Hassell-Varley'
    cls_ramas = [ATipoI, MTipoI]

    def eval(símismo, paso):
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
    unids = None
    inter = ['presa', 'huésped']


class TipoIIHasselVarley(EcuaciónDepred):
    """
    Depredación de respuesta funcional Tipo II con dependencia Hassell-Varley.
    """

    nombre = 'Tipo I_Hassell-Varley'
    cls_ramas = [ATipoII, BTipoII, MTipoII]

    def eval(símismo, paso):
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
    unids = None
    inter = ['presa', 'huésped']


class TipoIIIHasselVarley(EcuaciónDepred):
    """
    Depredación de respuesta funcional Tipo III con dependencia Hassell-Varley.
    """

    nombre = 'Tipo I_Hassell-Varley'
    cls_ramas = [ATipoIII, BTipoIII, MTipoIII]

    def eval(símismo, paso):
        dens_depred = símismo.dens_depred()
        cf = símismo.cf
        return np.multiply(dens / dens_depred ** cf['m'], cf['a'] / (dens / dens_depred ** cf['m'] + cf['b']))
