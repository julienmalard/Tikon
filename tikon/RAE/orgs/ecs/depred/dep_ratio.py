from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class TipoIDR(Ecuación):
    nombre = 'Tipo I_Dependiente ratio'
    _cls_ramas = [ATipoI]


class ATipoII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class BTipoII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIDR(Ecuación):
    nombre = 'Tipo II_Dependiente ratio'
    _cls_ramas = [ATipoII, BTipoII]


class ATipoIII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class BTipoIII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIIDR(Ecuación):
    nombre = 'Tipo III_Dependiente ratio'
    _cls_ramas = [ATipoIII, BTipoIII]
