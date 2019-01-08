from tikon.rae.orgs.organismo import EtapaFantasma
from tikon.result.res import Resultado


class ResultadoRed(Resultado):

    def finalizar(símismo):
        if símismo.matr_t:
            ejes_etps = [eje for eje in símismo.ejes().items() if eje[0] in ['etapa', 'víctima']]
            for nmb, eje in ejes_etps:
                etps = eje.índs
                fantasmas = [e for e in etps if isinstance(e, EtapaFantasma)]
                for etp in fantasmas:
                    val = símismo.matr_t.obt_valor(índs={nmb: etp})
                    símismo.matr_t.poner_valor(val, rel=True, índs={nmb: etp.etp_espejo})
