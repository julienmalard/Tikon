import numpy as np
from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónDepred


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']
    unids = None


class TipoIDR(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo I con dependencia en el ratio de presa a depredador.
    
    Generalmente no recomendable. Incluido aquí por puro interés científico.

    .. math::
       f(P,D) = a*P/D
    """

    nombre = 'Tipo I_Dependiente ratio'
    cls_ramas = [ATipoI]

    def eval(símismo, paso, sim):
        dens = símismo.dens_pobs(sim, filtrar=False)
        dens_depred = símismo.dens_pobs(sim)
        return (dens / dens_depred) * símismo.cf['a']


class ATipoII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']
    unids = 'presa depredador -1 ha -1'


class BTipoII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = 'presa depredador -1'


class TipoIIDR(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo II con dependencia en el ratio de presa a depredador.
    
    .. math::
       f(P,D) = a*(P/D) / ((P/D) + b)
    
    """
    nombre = 'Tipo II_Dependiente ratio'
    cls_ramas = [ATipoII, BTipoII]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        dens = símismo.dens_pobs(sim, filtrar=False)
        dens_depred = símismo.dens_pobs(sim)
        ratio = dens / dens_depred
        return ratio * cf['a'] / (ratio + cf['b'])


class ATipoIII(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']
    unids = 'presa depredador -1 ha -1'


class BTipoIII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = 'presa 2 depredador -2'


class TipoIIIDR(EcuaciónDepred):
    """
    Depredación de respuesta funcional tipo III con dependencia en el ratio de presa a depredador.
    
    .. math::
       f(P,D) = a*(P/D)^2 / ((P/D)^2 + b)
    """
    nombre = 'Tipo III_Dependiente ratio'
    cls_ramas = [ATipoIII, BTipoIII]

    def eval(símismo, paso, sim):
        cf = símismo.cf

        dens = símismo.dens_pobs(sim, filtrar=False)
        dens_depred = símismo.dens_pobs(sim)
        ratio_2 = np.square(dens / dens_depred)
        return ratio_2 * cf['a'] / (ratio_2 + cf['b'])
