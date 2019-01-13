import numpy as np

from tikon.rae.orgs.organismo import EtapaFantasma
from tikon.result.res import Resultado


class ResultadoRed(Resultado):
    ejes_etps = ['etapa']

    def finalizar(símismo):
        if símismo.matr_t:
            ejes_etps = [eje for eje in símismo.ejes().items() if eje[0] in símismo.ejes_etps]
            for nmb, eje in ejes_etps:
                etps = eje.índs
                fantasmas = [e for e in etps if isinstance(e, EtapaFantasma)]
                for etp in fantasmas:
                    val = símismo.matr_t.obt_valor(índs={nmb: etp})

                    # Agregamos etapas fantasmas a la etapa juvenil del parasitoide (etapa espejo)
                    if etp.etp_espejo in eje:  # para hacer: arreglar para ecuaciones no activadas en etapas espejos
                        fants_espejo = [f for f in fantasmas if f.etp_espejo == etp.etp_espejo]
                        rel = etp is not fants_espejo[0]
                        símismo.matr_t.poner_valor(val, rel=rel, índs={nmb: etp.etp_espejo})

                    # Agregamos etapas fantasmas a las etapas originales de los huéspedes
                    if etp.etp_hués in eje:
                        símismo.matr_t.poner_valor(val, rel=True, índs={nmb: etp.etp_hués})

    def reinic(símismo):
        super().reinic()

        etps = símismo.ejes()['etapa'].índs

        fantasmas = [e for e in etps if isinstance(e, EtapaFantasma)]

        def buscar_fants(e):
            return [f for f in fantasmas if f.etp_espejo is e]

        etps_espejo = [(e, buscar_fants(e)) for e in etps if buscar_fants(e)]

        def obt_val(e):
            return símismo.obt_valor_t(0, {'etapa': e})

        # para hacer: reorganizar si etps_espejo se convierten en grupos de etapas
        for f in fantasmas:
            val_f = obt_val(f)
            símismo.poner_valor(-val_f, rel=True, índs={'etapa': f.etp_hués})

        for esp, fants in etps_espejo:
            val_eps = obt_val(esp)
            fants_disp = np.array([obt_val(f.etp_hués) for f in fants])
            aloc = val_eps / np.sum(fants_disp, axis=0) * fants_disp
            # resto = np.sum(aloc - np.floor(aloc), axis=0).astype(int)  # para hacer: no necesario si poblaciones frac
            aloc = np.floor(aloc)
            for a, f in zip(aloc, fants):
                símismo.poner_valor(a, rel=True, índs={'etapa': f})
                símismo.poner_valor(-a, rel=True, índs={'etapa': f.etp_hués})

        símismo.actualizar()


class ResultadoDepred(ResultadoRed):
    ejes_etps = ['etapa', 'víctima']


class ResultadoEdad(ResultadoRed):

    def finalizar(símismo):
        pass
