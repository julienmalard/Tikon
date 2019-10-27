from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónDepred


class ATipoI(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = None


class MTipoI(Parám):
    nombre = 'm'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = None


class TipoIHasselVarley(EcuaciónDepred):
    """
    Depredación de respuesta funcional Tipo I con dependencia Hassell-Varley.
    P en las respuestas funcionales se cambia a P/(D^m)
    
    .. math::
       f(P,D) = a*P/(D^m)

    References
    ----------
    .. [1] M.P. Hassell, G.C. Varley. New inductive population model for insect parasites and its bearing on
           biological control. Nature, 223 (1969), pp. 1133–1136

    """
    nombre = 'Tipo I_Hassell-Varley'
    cls_ramas = [ATipoI, MTipoI]

    def eval(símismo, paso, sim):
        cf = símismo.cf

        dens = símismo.dens_pobs(sim, filtrar=False)
        dens_depred = símismo.dens_pobs(sim)
        return (dens / dens_depred ** cf['m']) * cf['a']


class ATipoII(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = None


class BTipoII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = None


class MTipoII(Parám):
    nombre = 'm'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = None


class TipoIIHasselVarley(EcuaciónDepred):
    """
    Depredación de respuesta funcional Tipo II con dependencia Hassell-Varley.
    
    .. math::
       f(P,D) = a*P/(D^m) / (P/(D^m) + b)
    """

    nombre = 'Tipo I_Hassell-Varley'
    cls_ramas = [ATipoII, BTipoII, MTipoII]

    def eval(símismo, paso, sim):
        cf = símismo.cf

        dens = símismo.dens_pobs(sim, filtrar=False)
        dens_depred = símismo.dens_pobs(sim)
        ratio = dens / dens_depred ** cf['m']
        return ratio * cf['a'] / (ratio + cf['b'])


class ATipoIII(Parám):
    nombre = 'a'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = None


class BTipoIII(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = None


class MTipoIII(Parám):
    nombre = 'm'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = None


class TipoIIIHasselVarley(EcuaciónDepred):
    """
    Depredación de respuesta funcional Tipo III con dependencia Hassell-Varley.
    
    .. math::
       f(P,D) = a*P/(D^m)^2 / (P/(D^m)^2 + b)

    """

    nombre = 'Tipo I_Hassell-Varley'
    cls_ramas = [ATipoIII, BTipoIII, MTipoIII]

    def eval(símismo, paso, sim):
        cf = símismo.cf

        dens = símismo.dens_pobs(sim, filtrar=False)
        dens_depred = símismo.dens_pobs(sim)
        ratio = (dens / dens_depred ** cf['m']) ** 2
        return ratio * cf['a'] / (ratio + cf['b'])
