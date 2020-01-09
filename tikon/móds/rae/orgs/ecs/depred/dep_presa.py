import numpy as np

from tikon.ecs.árb_mód import Parám
from ._plntll_ec import EcuaciónDepred


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']
    unids = 'depredador -1'


class TipoIDP(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo I con dependencia en la población de la presa.

    Generalmente no recomendable. Incluido aquí por puro interés científico.

    .. math::
       f(P) = a*P
    """

    nombre = 'Tipo I_Dependiente presa'
    cls_ramas = [ATipoI]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        dens = símismo.dens_pobs(sim, filtrar=False)
        return dens * cf['a']


class ATipoII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']
    unids = 'presa depredador -1 ha -1'


class BTipoII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = 'presa ha -1'


class TipoIIDP(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo II con dependencia en la población de la presa.
    
    .. math::
       f(P) = a*P / (P + b)

    """

    nombre = 'Tipo II_Dependiente presa'
    cls_ramas = [ATipoII, BTipoII]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        dens = símismo.dens_pobs(sim, filtrar=False)
        return dens * cf['a'] / (dens + cf['b'])


class ATipoIII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']
    unids = 'presa depredador -1 ha -1'


class BTipoIII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = 'presa 2 ha -2'


class TipoIIIDP(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo III con dependencia en la población de la presa.
    
    .. math::
       f(P) = a*P^2 / (P^2 + b)

    """

    nombre = 'Tipo III_Dependiente presa'
    cls_ramas = [ATipoIII, BTipoIII]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        dens = símismo.dens_pobs(sim, filtrar=False)
        return dens ** 2 * cf['a'] / (dens ** 2 + cf['b'])
