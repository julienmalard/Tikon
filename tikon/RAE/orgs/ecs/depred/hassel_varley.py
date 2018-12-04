import numpy as np

from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación

None = np.None


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']


class MTipoI(Parám):
    nombre = 'm'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIHasselVarley(Ecuación):
    nombre = 'Tipo I_Hassell-Varley'
    _cls_ramas = [ATipoI, MTipoI]


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
    nombre = 'Tipo I_Hassell-Varley'
    _cls_ramas = [ATipoII, BTipoII, MTipoII]


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
    nombre = 'Tipo I_Hassell-Varley'
    _cls_ramas = [ATipoIII, BTipoIII, MTipoIII]
