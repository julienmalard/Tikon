import os

import numpy as np

from tikon.ecs.aprioris import APrioriDens
from tikon.ecs.árb_mód import Parám
from tikon.exper.inic import MnjdrInicExper, MnjdrInicMód
from tikon.rae.orgs.organismo import EtapaFantasma


class Exper(object):
    def __init__(símismo, nombre, obs=None):
        símismo.nombre = nombre
        símismo.obs = MnjdrObsExper(obs)
        símismo.controles = MnjdrControlesExper()
        símismo.inic = MnjdrInicExper()

    def n_días(símismo):
        return símismo.obs.n_días(símismo.f_inic())

    def f_inic(símismo):
        return símismo.obs.f_inic()

    def obt_control(símismo, var):
        return símismo.controles[var]

    def obt_inic(símismo, mód, var=None):
        try:
            inic_mód = símismo.inic[mód]
        except KeyError:
            inic_mód = MnjdrInicMód()
            símismo.inic._inic[str(mód)] = inic_mód
        return inic_mód.obt_inic(var)

    def agregar_obs(símismo, obs):
        símismo.obs.agregar_obs(obs)

    def obtener_obs(símismo, mód, var=None):
        if var:
            return símismo.obs[mód][var]
        return símismo.obs[mód]

    def iniciar_estruc(símismo, tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés):

        # para hacer: limpiar, y agregar fecha de inicio y parcelas. generalizar y quitar mención de 'red' y 'etapa'
        # TODO LO QUE SIGUE ES CÓDIGO TEMPORARIO Y HORRIBLEMENTE INELEGANTE, INEFICAZ, E INCÓMODO1

        try:
            red = mnjdr_móds['red']
        except KeyError:
            return []

        etps = [e for e in red.info_etps.etapas if not isinstance(e, EtapaFantasma)]
        # para hacer: limpiar, y agregar fecha de inicio y parcelas. generalizar y quitar mención de 'red' y 'etapa'
        obs = símismo.obtener_obs(red, 'Pobs')
        for etp in etps:
            try:
                obs.obt_val_t(0, {'etapa': etp})
            except ValueError:
                class prm(Parám):
                    nombre = 'inic'
                    líms = (0, None)

                prm_coso = prm.para_coso(None)
                apriori = APrioriDens((0, np.max(obs.obt_val_t(0))), 0.9)
                prm_coso.espec_a_priori(apriori)
                símismo.inic.agregar_prm(
                    mód='red', var='Pobs', índs={'etapa': etp}, prm_base=prm_coso, tmñ=n_rep_parám
                )

    def paráms(símismo):
        return símismo.inic.vals_paráms()

    def guardar_calib(símismo, directorio=''):
        archivo = os.path.join(directorio, símismo.nombre)
        símismo.inic.guardar_calib(archivo)


_controles_auto = {  # para hacer: más bonito
    'parcelas': ['1'],
    'superficies': np.array([1.])
}


class MnjdrControlesExper(object):
    def __init__(símismo):
        símismo.d_vals = _controles_auto

    def __getitem__(símismo, itema):
        return símismo.d_vals[itema]


class MnjdrObsExper(object):
    def __init__(símismo, obs=None):
        símismo._obs = {}
        if obs is not None:
            símismo.agregar_obs(obs)

    def agregar_obs(símismo, obs):
        if isinstance(obs, list):
            for ob in obs:
                símismo.agregar_obs(ob)

        mód = str(obs.mód)
        if mód not in símismo._obs:
            símismo._obs[mód] = MnjdrObsMód()
        símismo._obs[mód].agregar_obs(obs, obs.var)

    def f_inic(símismo):
        fechas = [f for f in [obs.f_inic() for obs in símismo] if f]
        if fechas:
            return min(fechas)

    def n_días(símismo, f_inic):
        días = [f for f in [obs.n_días(f_inic) for obs in símismo] if f]
        if días:
            return max(días)

    def __iter__(símismo):
        for obs in símismo._obs.values():
            yield obs

    def __getitem__(símismo, itema):
        return símismo._obs[str(itema)]


class MnjdrObsMód(object):
    def __init__(símismo):
        símismo._obs = {}

    def agregar_obs(símismo, obs, var):
        símismo._obs[var] = obs

    def f_inic(símismo):
        try:
            min([f for f in [obs.f_inic() for obs in símismo] if f])
        except ValueError:
            return None

    def n_días(símismo, f_inic):
        return max([obs.n_días(f_inic) for obs in símismo])

    def __contains__(símismo, itema):
        return itema in símismo._obs

    def __iter__(símismo):
        for obs in símismo._obs.values():
            yield obs

    def __getitem__(símismo, itema):
        return símismo._obs[str(itema)]
