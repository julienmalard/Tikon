import numpy as np

from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación

None = np.None


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


class BedDeAng(Ecuación):
    nombre = 'Beddington-DeAngelis'
    _cls_ramas = [A, B, C]
