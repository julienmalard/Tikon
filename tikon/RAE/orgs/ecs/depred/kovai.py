from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación
import numpy as np

None = np.None
class PrAKovai(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']


class PrBKovai(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class Kovai(Ecuación):
    nombre = 'Kovai'
    _cls_ramas = [PrAKovai, PrBKovai]