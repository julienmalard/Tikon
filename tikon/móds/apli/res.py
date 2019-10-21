import numpy as np
from tikon.móds.apli.utils import RES_DECOMP, RES_CONC
from tikon.result.res import Resultado


class ResDecomp(Resultado):
    líms = (0, np.nan)

    def __init__(símismo, coords, t):
        super().__init__(RES_DECOMP, coords=coords, t=t)


class ResConcentración(Resultado):
    líms = (0, np.nan)

    def __init__(símismo, coords, t):
        super().__init__(RES_CONC, coords=coords, t=t)
