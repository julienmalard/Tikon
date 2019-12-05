import os
from inspect import isclass

from tikon.calibrador.spotpy_ import EVM
from tikon.ecs import Parám
from tikon.datos.proc import ens, gen_proc

from .calibs import _gen_espec_calibs
from .coso import Coso
from .exper import Exper
from .módulo import Módulo
from .simul import Simulación


class Modelo(object):

    def __init__(símismo, módulos):
        if isinstance(módulos, Módulo) or (isclass(módulos) and issubclass(módulos, Módulo)):
            módulos = [módulos]
        módulos = [m() if isclass(m) else m for m in módulos]

        símismo.módulos = {str(m): m for m in módulos}

    def simular(símismo, nombre, exper, t=None, calibs=None, reps=None, vars_interés=None, depurar=False):

        calibs = _gen_espec_calibs(calibs, aprioris=True, heredar=True, corresp=True)
        reps = _gen_reps(reps)

        simul = Simulación(
            nombre=nombre, modelo=símismo, t=t, exper=exper, calibs=calibs, reps=reps,
            vars_interés=vars_interés
        )
        simul.simular(depurar=depurar)
        return simul

    def calibrar(
            símismo, nombre, exper, t=None, n_iter=300, calibrador=EVM(), proc=ens, calibs=None, reps=None,
            paráms=None
    ):

        calibs = _gen_espec_calibs(calibs, aprioris=True, heredar=True, corresp=False)

        reps = _gen_reps(reps, calib=True, paráms=paráms)
        sim = Simulación(nombre, modelo=símismo, exper=exper, t=t, calibs=calibs, reps=reps, vars_interés=None)
        proc = gen_proc(proc)

        def func_opt():
            sim.iniciar()
            sim.correr()
            sim.cerrar()
            return sim.procesar_calib(proc)

        paráms_calib = símismo._filtar_paráms(sim.paráms, paráms)
        calibrador.calibrar(
            nombre, func=func_opt, paráms=paráms_calib, calibs=calibs, n_iter=n_iter
        )

    def guardar_calibs(símismo, directorio=''):
        for m in símismo:
            símismo[m].guardar_calibs(directorio=os.path.join(directorio, str(m)))

    def cargar_calibs(símismo, directorio=''):
        for m in símismo:
            símismo[m].cargar_calibs(directorio=os.path.join(directorio, str(m)))

    def _filtar_paráms(símismo, paráms, en):
        if en is None:
            return paráms
        if isinstance(en, (str, Módulo, Coso, Parám, Exper)):
            en = [en]
        en = [next(m for nmbr, m in símismo.módulos.items() if nmbr == x) if isinstance(x, str) else x for x in en]
        return [
            prm for prm in paráms
            if any(
                prm.prm.coso == x if isinstance(x, Coso)
                else prm.prm == x if isinstance(x, Parám)
                else prm.prm.coso == x if isinstance(x, Exper)
                else prm.prm.coso in x
                for x in en)
        ]

    def __getitem__(símismo, itema):
        return símismo.módulos[itema]

    def __iter__(símismo):
        for m in símismo.módulos:
            yield m

    def __contains__(símismo, itema):
        return itema in símismo.módulos


def _gen_reps(reps, calib=False, paráms=None):
    if calib:
        if paráms:
            base = {'paráms': 15, 'estoc': 5}
        else:
            base = {'paráms': 1, 'estoc': 30}
    else:
        base = {'paráms': 15, 'estoc': 5}
    if reps is None:
        return base
    if isinstance(reps, int):
        return {'paráms': reps, 'estoc': reps}

    extras = {ll for ll in reps if ll not in base}
    if extras:
        raise ValueError('{extras} no es valor aceptable para eje de repetición.'.format(extras=', '.join(extras)))
    base.update(reps)
    return base
