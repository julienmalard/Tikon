import numpy as np
from tikon.central.res import Resultado
from tikon.móds.rae.orgs.organismo import EtapaFantasma
from tikon.móds.rae.red.utils import RES_DEPR, RES_POBS, EJE_VÍCTIMA, RES_EDAD, RES_CREC, RES_REPR, RES_MRTE, \
    RES_TRANS, RES_MOV, RES_ESTOC, EJE_ETAPA
from tikon.result import EJE_DEST


class ResultadoRed(Resultado):
    líms = (0, np.inf)
    ejes_etps = [EJE_ETAPA]
    unids = 'individuos / día'

    def __init__(símismo, sim, coords, vars_interés):
        if EJE_ETAPA not in coords:  # Hay que verificar porque `Cohortes` lo implementa sí mismo
            coords = {EJE_ETAPA: sim.ecs.cosos_en_categ(símismo.nombre), **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

    @property
    def nombre(símismo):
        raise NotImplementedError

    def cerrar(símismo):
        for eje in símismo.ejes_etps:
            etps = símismo.datos_t[eje]

            fantasmas = [e for e in símismo.datos_t[eje].values if isinstance(e, EtapaFantasma)]

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


class ResPobs(ResultadoRed):
    nombre = RES_POBS
    unids = 'individuos'
    inicializable = True

    def iniciar(símismo):
        super().iniciar()

        np.round(símismo._matr, out=símismo._matr)

        etps = símismo.ejes()[EJE_ETAPA].índs

        fantasmas = [e for e in etps if isinstance(e, EtapaFantasma)]

        def buscar_fants(e):
            return [f for f in fantasmas if f.etp_espejo is e]

        etps_espejo = [(e, buscar_fants(e)) for e in etps if buscar_fants(e)]

        def obt_val(e):
            return símismo.obt_valor({EJE_ETAPA: e})

        # para hacer: reorganizar si etps_espejo se convierten en grupos de etapas
        for f in fantasmas:
            val_f = obt_val(f)
            símismo.poner_valor(-val_f, rel=True, índs={EJE_ETAPA: f.etp_hués})

        for esp, fants in etps_espejo:
            val_eps = obt_val(esp)
            fants_disp = np.array([obt_val(f.etp_hués) for f in fants])
            aloc = val_eps / np.sum(fants_disp, axis=0) * fants_disp
            # resto = np.sum(aloc - np.floor(aloc), axis=0).astype(int)  # para hacer: no necesario si poblaciones frac
            aloc = np.floor(aloc)
            for a, f in zip(aloc, fants):
                símismo.poner_valor(a, rel=True, índs={EJE_ETAPA: f})
                símismo.poner_valor(-a, rel=True, índs={EJE_ETAPA: f.etp_hués})


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
        pass


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

    def __init__(símismo, sim, coords):
        coords = {EJE_DEST: sim.exper.controles['parcelas'], **coords}
        super().__init__(sim=sim, coords=coords)


class ResEstoc(ResultadoRed):
    nombre = RES_ESTOC
    líms = None  # La estocasticidad puede ser positiva o negativa
