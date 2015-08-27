from pymc import *
import numpy as np


def inic_calib(datos,):

    precisión = Exponential()
    @deterministic
    def promedio(coso):
        return
    variable = Normal('var', mu=promedio, tau=precisión, value=datos, observed=True)

