import numpy as np
from scipy.stats import expon
from tikon.central.res import Resultado
from tikon.ecs.aprioris import APrioriDist
from tikon.móds.rae.utils import RES_DEPR, RES_POBS, EJE_VÍCTIMA, RES_EDAD, RES_CREC, RES_REPR, RES_MRTE, RES_TRANS, \
    RES_MOV, \
    RES_ESTOC, EJE_ETAPA
from tikon.utils import EJE_DEST

from ...orgs.organismo import EtapaFantasma


class ResultadoRed(Resultado):
    líms = (0, np.inf)
    ejes_etps = [EJE_ETAPA]
    unids = 'individuos / día'

    def __init__(símismo, sim, coords, vars_interés):
        if EJE_ETAPA not in coords:  # Hay que verificar porque `Cohortes` lo implementa sí mismo
            coords = {EJE_ETAPA: [x for x in sim.ecs.cosos_en_categ(símismo.nombre)], **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

    @property
    def nombre(símismo):
        raise NotImplementedError

    def cerrar(símismo):
        super().cerrar()
        for eje in símismo.ejes_etps:
            fantasmas = [e for e in símismo.datos_t[eje].values if isinstance(e, EtapaFantasma)]

            for etp in fantasmas:
                val = símismo.datos_t.loc[{eje: etp}]

                # Agregamos etapas fantasmas a la etapa juvenil del parasitoide (etapa espejo)
                if etp.etp_espejo in símismo.datos_t[eje]:
                    símismo.datos_t.loc[{eje: etp.etp_espejo}] += val

                # Agregamos etapas fantasmas a las etapas originales de los huéspedes
                if etp.etp_hués in símismo.datos_t[eje]:
                    símismo.datos_t.loc[{eje: etp.etp_hués}] += val


class ResPobs(ResultadoRed):
    nombre = RES_POBS
    unids = 'individuos'
    inicializable = True
    apriori = APrioriDist(expon(scale=3e6))

    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_ETAPA: sim.etapas, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

    def iniciar(símismo):
        super().iniciar()
        símismo.poner_valor(np.round(símismo.datos))


class ResDepred(ResultadoRed):
    nombre = RES_DEPR

    ejes_etps = [EJE_ETAPA, EJE_VÍCTIMA]

    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_VÍCTIMA: sim.víctimas, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)


class ResEdad(ResultadoRed):
    nombre = RES_EDAD
    unids = 'días equivalentes'

    def cerrar(símismo):
        Resultado.cerrar(símismo)


class ResCrec(ResultadoRed):
    nombre = RES_CREC
    líms = None  # Crecimiento puede ser positivo o negativo


class ResRepr(ResultadoRed):
    nombre = RES_REPR


class ResMuerte(ResultadoRed):
    nombre = RES_MRTE


class ResTrans(ResultadoRed):
    nombre = RES_TRANS


class ResMov(ResultadoRed):
    nombre = RES_MOV
    líms = None  # Movimiento puede ser positivo (imigración) o negativo (emigración)

    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_DEST: sim.exper.controles['parcelas'], **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)


class ResEstoc(ResultadoRed):
    nombre = RES_ESTOC
    líms = None  # La estocasticidad puede ser positiva o negativa
