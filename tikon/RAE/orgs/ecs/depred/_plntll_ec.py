from .._plntll_ec import EcuaciónOrg


class EcuaciónDepred(EcuaciónOrg):

    def obt_dens_pobs(símismo, filtrar=True):

        pobs = símismo.obt_val_mód('Pobs', filtrar=filtrar)
        superficies = símismo.obt_val_control('superficies')
        return pobs / superficies.reshape((*superficies.shape, *[1]*(len(pobs.shape)-1)))

    def eval(símismo, paso):
        raise NotImplementedError
