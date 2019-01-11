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
                        rel = etp is not fantasmas[0]
                        símismo.matr_t.poner_valor(val, rel=rel, índs={nmb: etp.etp_espejo})

                    # Agregamos etapas fantasmas a las etapas originales de los huéspedes
                    if etp.etp_hués in eje:
                        símismo.matr_t.poner_valor(val, rel=True, índs={nmb: etp.etp_hués})


class ResultadoDepred(ResultadoRed):
    ejes_etps = ['etapa', 'víctima']


class ResultadoEdad(ResultadoRed):

    def finalizar(símismo):
        pass
