import os
from datetime import timedelta

from .control import ControlesExper
from .datos import DatosExper
from .parc import GrupoParcelas
from .parc import Parcela
from .paráms_exper import ParámsExper
from .tiempo import Tiempo, gen_tiempo


class Exper(object):
    def __init__(símismo, nombre, parcelas, obs=None):
        símismo.nombre = nombre
        símismo.datos = DatosExper(nombre)

        símismo.parcelas = _extract_parcelas(parcelas)
        if len(símismo.parcelas) != len({str(p) for p in símismo.parcelas}):
            raise ValueError(
                'Parcelas con nombres idénticos en "{p}".'.format(p=', '.join([str(p) for p in símismo.parcelas]))
            )
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

    def borrar_calib(símismo, nombre):
        símismo.datos.borrar_calib(nombre)

    def renombrar_calib(símismo, nombre, nuevo):
        símismo.datos.renombrar_calib(nombre, nuevo)

    def guardar_calibs(símismo, directorio=''):
        archivo = os.path.join(directorio, símismo.nombre + '.json')
        símismo.datos.guardar_calibs(archivo)

    def cargar_calibs(símismo, directorio=''):
        if os.path.splitext(directorio)[1] == '.json':
            archivo = directorio
        else:
            archivo = os.path.join(directorio, símismo.nombre + '.json')
        símismo.datos.cargar_calibs(archivo)


def _extract_parcelas(parcelas):
    parcelas = [parcelas] if isinstance(parcelas, (Parcela, GrupoParcelas)) else parcelas
    l_prcs = []
    for prc in parcelas:
        if isinstance(prc, Parcela):
            l_prcs.append(prc)
        else:
            l_prcs += prc.parcelas
    return l_prcs
