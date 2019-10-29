import numpy as np
from tikon.móds.apli.utils import RES_DECOMP, RES_CONC
from tikon.result.res import Resultado


class ResDecomp(Resultado):
    líms = (0, np.nan)
    nombre = RES_DECOMP


class ResConcentración(Resultado):
    líms = (0, np.nan)
    nombre = RES_CONC
