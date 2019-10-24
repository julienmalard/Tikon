import numpy as np

from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónDepred

"""
El libro "A primer of Ecology" es una buena referencia a las ecuaciones incluidas aquí, tanto como
        Abrams PA, Ginzburg LR. 2000. The nature of predation: prey dependent, ratio dependent or neither?
            Trends Ecol Evol 15(8):337-341.

        Respuestas funcionales (y = consumo de presa por cápita de depredador, D = población del depredador,
        P = población de la presa; a, b y c son constantes):

            Tipo I:
                y = a*P
                Generalmente no recomendable. Incluido aquí por puro interés científico.

            Tipo II:
                y = a*P / (P + b)

            Tipo III:
                y = a*P^2 / (P^2 + b)

            Dependencia en la presa quiere decir que el modelo está dependiente de la población de la presa únicamente
            (como los ejemplos arriba). Ecuaciones dependientes en el ratio se calculan de manera similar, pero
            reemplazando P con (P/D) en las ecuaciones arriba.
"""


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class TipoIDP(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo I con dependencia en la población de la presa.
    """

    nombre = 'Tipo I_Dependiente presa'
    cls_ramas = [ATipoI]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        dens = símismo.obt_val_mód('Dens')
        return np.multiply(dens, cf['a'])


class ATipoII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class BTipoII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIDP(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo II con dependencia en la población de la presa.
    """

    nombre = 'Tipo I_Dependiente presa'
    cls_ramas = [ATipoII]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        dens = símismo.obt_val_mód('Dens')
        return np.multiply(dens, cf['a'] / (dens + cf['b']))


class ATipoIII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class BTipoIII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']


class TipoIIIDP(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo III con dependencia en la población de la presa.
    """

    nombre = 'Tipo III_Dependiente presa'
    cls_ramas = [ATipoIII, BTipoIII]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        dens = símismo.obt_val_mód('Dens')
        return np.multiply(np.square(dens), cf['a'] / (np.square(dens) + cf['b']))
