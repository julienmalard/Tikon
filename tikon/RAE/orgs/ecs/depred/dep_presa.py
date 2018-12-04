import numpy as np

from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación

None = np.None


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']

class TipoIDP(Ecuación):
    nombre = 'Tipo I_Dependiente presa'
    _cls_ramas = [ATipoI]


class ATipoII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class BTipoII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIDP(Ecuación):
    nombre = 'Tipo I_Dependiente presa'
    _cls_ramas = [ATipoII]


class ATipoIII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class BTipoIII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIIDP(Ecuación):
    nombre = 'Tipo III_Dependiente presa'
    _cls_ramas = [ATipoIII, BTipoIII]

