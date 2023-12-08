import numpy as np
from frozendict import frozendict
from scipy.stats import expon, uniform

from tikon.central.res import Resultado
from tikon.ecs.aprioris import APrioriDist, APrioriDens
from tikon.móds.rae.utils import RES_DEPR, RES_POBS, EJE_VÍCTIMA, RES_EDAD, RES_CREC, RES_REPR, RES_MRTE, RES_TRANS, \
    RES_MOV, \
    RES_ESTOC, EJE_ETAPA
from tikon.utils import EJE_DEST, EJE_TIEMPO
from ...orgs.insectos.paras import EtapaJuvenilParasitoide
from ...orgs.etapa import EtapaFantasma


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
        for eje in símismo.ejes_etps:
            fantasmas = [e for e in símismo._datos_t.coords[eje] if isinstance(e, EtapaFantasma)]
            paras_juv = [e for e in símismo._datos_t.coords[eje] if isinstance(e, EtapaJuvenilParasitoide)]
            if paras_juv:
                símismo._datos_t.loc[{eje: paras_juv}] = 0

            for etp in fantasmas:
                val = símismo._datos_t.loc[frozendict({eje: id(etp)})]

                # Agregamos etapas fantasmas a la etapa juvenil del parasitoide (etapa espejo)
                if etp.etp_espejo in símismo._datos_t.coords[eje]:
                    val.coords[eje] = [etp.etp_espejo]
                    símismo._datos_t += val

                # Agregamos etapas fantasmas a las etapas originales de los huéspedes
                if etp.etp_hués in símismo._datos_t.coords[eje]:
                    val.coords[eje] = [etp.etp_hués]
                    símismo._datos_t += val

        super().cerrar()


class ResPobs(ResultadoRed):
    nombre = RES_POBS
    unids = 'individuos'
    inicializable = True
    apriori = APrioriDist(expon(scale=3e6))

    def __init__(símismo, sim, coords, vars_interés):
        coords = {EJE_ETAPA: sim.etapas, **coords}
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

    def apriori_de_obs(símismo, obs, índ):
        etp = índ[EJE_ETAPA]

        def _extr_ref(e=None):
            if e:
                índ_e = {EJE_ETAPA: e, **{ll: v for ll, v in índ.items() if ll != EJE_ETAPA}}
            else:
                índ_e = índ
            datos_obs = [o_.datos.loc[índ_e].dropna(EJE_TIEMPO)[{EJE_TIEMPO: 0}] for o_ in obs if índ_e in o_]
            return (np.mean(datos_obs), max(np.std(datos_obs), np.mean(datos_obs)*.15, 1)) if datos_obs else None

        ref = _extr_ref()

        if isinstance(etp, EtapaJuvenilParasitoide):
            return APrioriDist(uniform(0, 1))
        if ref:
            mín = max(0, ref[0] - ref[1])
            return APrioriDens((mín, ref[0] + ref[1]), .80)
        if isinstance(etp, EtapaFantasma):
            ref_espejo = _extr_ref(etp.etp_espejo)
            ref_huésped = _extr_ref(etp.etp_hués)

            co_huéspedes = símismo.sim.mód.huéspedes(etp.org)
            if ref_espejo:
                ref_espejo = (ref_espejo[0]/len(co_huéspedes), ref_espejo[1]/len(co_huéspedes))
            if ref_espejo and ref_huésped:
                ref_mín = sorted([ref_espejo, ref_huésped])[0]
            else:
                ref_mín = ref_espejo or ref_huésped
            if ref_mín:
                mín = max(0, ref_mín[0] - ref_mín[1])
                return APrioriDens((mín, ref_mín[0] + ref_mín[1]), .80)

    def iniciar(símismo):
        super().iniciar()
        símismo.datos.fi(np.round)


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
