import numpy as np

from .._plntll_ec import EcuaciónOrg


class EcuaciónDepred(EcuaciónOrg):
    _nombre_res = 'Depredación'

    def obt_dens_pobs(símismo, filtrar=True, eje_extra='etapa'):

        pobs = símismo.pobs_etps(filtrar)
        superficies = símismo.obt_val_control('superficies')
        dens = pobs / superficies.reshape((*superficies.shape, *[1] * (len(pobs.shape) - 1)))  # para hacer: smplfcr

        if eje_extra is None:
            return dens
        else:
            eje = símismo.í_eje_res(eje_extra)
            return dens[tuple([slice(None)] * eje + [np.newaxis])]

    def eval(símismo, paso):
        raise NotImplementedError
