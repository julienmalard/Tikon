import os

import numpy as np
from tikon.ecs.aprioris import APrioriDens
from tikon.ecs.árb_mód import Parám
from tikon.estruc.tiempo import Tiempo, gen_tiempo
from tikon.exper.parc import Parcela
from tikon.móds.cultivo.extrn import ParcelasCultivoExterno

from .control import ControlesExper
from .datos import MnjdrInicExper, DatosExper


class Exper(object):
    def __init__(símismo, nombre, parcelas, obs=None):
        símismo.nombre = nombre
        símismo.datos = DatosExper()

        símismo.parcelas = _extract_parcelas(parcelas)
        símismo.controles = ControlesExper(símismo.parcelas)

        símismo.datos.agregar_obs(obs)

    def gen_t(símismo, t):
        if t is None:
            f_inic, f_final = símismo.datos.fechas()
            if not f_inic or not f_final:
                raise ValueError('Debes especificar fecha inicial y final para simulaciones sin observaciones.')

            return Tiempo(f_inic=f_inic, f_final=f_final)

        return gen_tiempo(t)


def _extract_parcelas(parcelas):
    parcelas = [parcelas] if isinstance(parcelas, (Parcela, ParcelasCultivoExterno)) else parcelas
    l_prcs = []
    for prc in parcelas:
        if isinstance(prc, Parcela):
            l_prcs.append(prc)
        else:
            l_prcs += prc.parcelas
    return l_prcs


class Exper(object):
    def __init__(símismo, obs=None):
        símismo.obs = MnjdrObsExper(obs)
        símismo.inic = MnjdrInicExper()

    def obt_inic(símismo, mód, var=None):
        try:
            inic_mód = símismo.inic[mód]
        except KeyError:
            inic_mód = símismo.inic.agregar_mód(mód)
        return inic_mód.obt_inic(var)

    def obtener_obs(símismo, mód, var=None):
        if var:
            return símismo.obs[mód][var]
        return símismo.obs[mód]

    def iniciar_estruc(símismo, tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés):

        # para hacer: limpiar, y agregar fecha de inicio y parcelas. generalizar y quitar mención de 'red' y 'etapa'
        # TODO LO QUE SIGUE ES CÓDIGO TEMPORARIO Y HORRIBLEMENTE INELEGANTE, INEFICAZ, E INCÓMODO

        try:
            red = mnjdr_móds['red']
        except KeyError:
            return []

        etps = red.etapas()
        # para hacer: limpiar, y agregar fecha de inicio y parcelas. generalizar y quitar mención de 'red' y 'etapa'
        obs = símismo.obtener_obs(red, 'Pobs')
        for etp in etps:
            try:
                obs.obt_val_t(0, {'etapa': etp})
            except ValueError:
                try:
                    # para hacer: necesitamos objeto para índs. Idealmente el mismo que para índs de matrices
                    prm_inic = símismo.inic['red']['Pobs'].obt_val({'etapa': str(etp)})

                except KeyError:
                    class prm(Parám):
                        nombre = 'inic'
                        líms = (0, None)

                    prm_coso = prm.para_coso(None)
                    apriori = APrioriDens((0, np.max(obs.obt_val_t(0))), 0.9)
                    prm_coso.espec_a_priori(apriori)
                    prm_inic = símismo.inic.agregar_prm(
                        mód='red', var='Pobs', índs={'etapa': str(etp)}, prm_base=prm_coso
                    )
                prm_inic.iniciar_prm(tmñ=n_rep_parám)

    def paráms(símismo):
        return símismo.inic.vals_paráms()

    def guardar_calib(símismo, directorio=''):
        archivo = os.path.join(directorio, símismo.nombre + '.json')
        símismo.inic.guardar_calib(archivo)

    def cargar_calib(símismo, directorio=''):
        if os.path.splitext(directorio)[1] == '.json':
            archivo = directorio
        else:
            archivo = os.path.join(directorio, símismo.nombre + '.json')
        símismo.inic.cargar_calib(archivo)


class MnjdrObsExper(object):
    def __init__(símismo, obs=None):
        símismo._obs = {}
        if obs is not None:
            símismo.agregar_obs(obs)

    def agregar_obs(símismo, obs):

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
