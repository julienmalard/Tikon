import os
from datetime import timedelta

from tikon.ecs.aprioris import APrioriDens
from tikon.ecs.árb_mód import Parám

from .control import ControlesExper
from .datos import MnjdrInicExper, DatosExper
from .parc import GrupoParcelas
from .parc import Parcela
from .paráms_exper import ParámsExper
from .tiempo import Tiempo, gen_tiempo


class Exper(object):
    def __init__(símismo, nombre, parcelas, obs=None):
        símismo.nombre = nombre
        símismo.datos = DatosExper(nombre)

        símismo.parcelas = _extract_parcelas(parcelas)
        símismo.controles = ControlesExper(símismo.parcelas)

        if obs:
            símismo.datos.agregar_obs(obs)

    def gen_t(símismo, t):
        f_inic, f_final = símismo.datos.fechas()
        if t is None:
            if not f_inic:
                raise ValueError('Debes especificar fecha inicial y final para simulaciones sin observaciones.')
            return Tiempo(f_inic=f_inic, f_final=f_final)

        if isinstance(t, int) and f_inic:
            return Tiempo(f_inic, f_inic + timedelta(days=t))
        return gen_tiempo(t)

    def gen_paráms(símismo, sim_exper):
        return ParámsExper(símismo, sim_exper)

    def guardar_calib(símismo, directorio=''):
        archivo = os.path.join(directorio, símismo.nombre + '.json')
        símismo.datos.guardar_calib(archivo)

    def cargar_calib(símismo, directorio=''):
        if os.path.splitext(directorio)[1] == '.json':
            archivo = directorio
        else:
            archivo = os.path.join(directorio, símismo.nombre + '.json')
        símismo.datos.cargar_calib(archivo)


def _extract_parcelas(parcelas):
    parcelas = [parcelas] if isinstance(parcelas, (Parcela, GrupoParcelas)) else parcelas
    l_prcs = []
    for prc in parcelas:
        if isinstance(prc, Parcela):
            l_prcs.append(prc)
        else:
            l_prcs += prc.parcelas
    return l_prcs


class Exper0(object):
    def __init__(símismo, obs=None):
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

        # para hacer: limpiar, y agregar fecha de inicio y parcelas. generalizar y quitar mención de 'red' y 'etapa'
        for etp in etps:
            try:
                # para hacer: necesitamos objeto para índs. Idealmente el mismo que para índs de matrices
                prm_inic = símismo.inic['red']['Pobs'].obt_val({'etapa': str(etp)})

            except KeyError:
                class prm(Parám):
                    nombre = 'inic'
                    líms = (0, None)

                prm_coso = prm.para_coso(None)
                apriori = APrioriDens()
                prm_coso.espec_apriori(apriori)
                prm_inic = símismo.inic.agregar_prm(
                    mód='red', var='Pobs', índs={'etapa': str(etp)}, prm_base=prm_coso
                )
            prm_inic.iniciar_prm(tmñ=n_rep_parám)

    def paráms(símismo):
        return símismo.inic.vals_paráms()
