from tikon.móds.rae.red.utils import RES_DEPR

from .._plntll import EcuaciónOrg


class EcuaciónDepred(EcuaciónOrg):
    _nombre_res = RES_DEPR

    def dens_pobs(símismo, sim, filtrar=True):
        pobs = símismo.pobs(filtrar)
        superficies = sim.obt_val_control('superficies')
        return pobs / superficies

    def eval(símismo, paso, sim):
        """
        Debe devolver la depredación en unidades de presas consumidas por depredador por hectárea.

        El libro [1]_ es una buena referencia para muchas de las ecuaciones incluidas aquí, tanto como
        [2]_.

        References
        ----------
        .. [1] "A primer of Ecology"
        .. [2] Abrams PA, Ginzburg LR. 2000. The nature of predation: prey dependent, ratio dependent or neither?
           Trends Ecol Evol 15(8):337-341.
        """
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
