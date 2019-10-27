from tikon.ecs.árb_mód import Parám

from ._plntll_ec import EcuaciónDepred


class A(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']
    unids = 'presa depredador -1 ha -1'


class B(Parám):
    nombre = 'b'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = 'presa ha -1'


class C(Parám):
    nombre = 'c'
    líms = (0, None)
    inter = ['presa', 'huésped']
    unids = 'presa depredador -1'


class BedDeAng(EcuaciónDepred):
    """
    Depredación de respuesta funcional Beddington-DeAngelis. Incluye dependencia en el depredador.

    Usamos una forma matemáticamente equivalente a la en el artículo, y que facilita el establecimiento de
    distribuciones a prioris para los parámetros:

    .. math::
       f(P) = aP / (b + P + cD)

    References
    ----------
    .. [1] J.R. Beddington. Mutual interference between parasites and its effect on searching efficiency. J.
           Anim. Ecol., 44 (1975), pp. 331–340
    .. [2] D.L. DeAngelis, et al. A model for trophic interaction Ecology, 56 (1975), pp. 881–892

    """
    nombre = 'Beddington-DeAngelis'
    cls_ramas = [A, B, C]

    def eval(símismo, paso, sim):
        cf = símismo.cf

        dens_depred = símismo.dens_pobs(sim)
        dens = símismo.dens_pobs(sim, filtrar=False)

        depred_etp = dens * cf['a'] / (cf['b'] + dens + cf['c'] * dens_depred)

        return depred_etp
