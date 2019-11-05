import os

from tikon.calibrador.spotpy_ import EVM
from tikon.estruc.calibs import _gen_espec_calibs
from tikon.estruc.simul import Simulación
from tikon.móds.cultivo.cult import Cultivo
from tikon.móds.manejo import Manejo
from tikon.sensib import gen_anlzdr_sensib


class Modelo(object):

    def __init__(símismo, módulos):
        símismo.módulos = {str(m): m for m in módulos}

    def simular(símismo, nombre, exper, t=None, calibs=None, reps=None, vars_interés=None):

        calibs = _gen_espec_calibs(calibs, aprioris=False, heredar=True, corresp=True)
        reps = _gen_reps(reps)

        return Simulación(
            nombre=nombre, módulos=símismo.módulos, t=t, exper=exper, calibs=calibs, reps=reps,
            vars_interés=vars_interés
        ).simular()

    def iniciar_estruc(símismo, días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám, vars_interés):

        # para hacer: ¿más elegante en general?
        símismo.exper.iniciar_estruc(
            símismo.tiempo, símismo.mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés
        )

        if llenar or True:  # para hacer: arreglar con calibraciones selectivas
            # para hacer: reorganizar sin paráms y exper
            símismo.mnjdr_móds.llenar_coefs(calibs, n_rep_parám=n_rep_parám)

    def sensib(
            símismo, exper, t=None, n=10, método='sobol', calibs=None, paso=1, n_rep_estoc=30,
            vars_interés=None, ops_mstr=None, ops_anlz=None
    ):
        ops_mstr = ops_mstr or {}
        ops_anlz = ops_anlz or {}
        calibs = _gen_espec_calibs(calibs, aprioris=True, heredar=True, corresp=False)

        sim = Simulación(símismo.módulos, exper=exper, t=t, reps=(n_rep_estoc, 1), vars_interés=vars_interés)

        anlzdr = gen_anlzdr_sensib(método, sim.paráms, calibs=calibs)

        anlzdr.aplicar_muestrea(n, ops=ops_mstr)

        sim.iniciar()
        sim.correr()
        sim.cerrar()

        return anlzdr.analizar(sim, ops=ops_anlz)

    def calibrar(
            símismo, nombre, exper, t=None, n_iter=300, calibrador=EVM, func=None, calibs=None, reps=None,
            paráms=None,
    ):

        reps = _gen_reps(reps, calib=True)
        sim = Simulación(nombre, símismo.módulos, exper=exper, t=t, reps=reps, vars_interés=None)

        def func_opt():
            sim.iniciar()
            sim.correr()
            return sim.procesar_calib(func)

        espec_calibs = _gen_espec_calibs(calibs, aprioris=True, heredar=True, corresp=False)
        espec_calibs_inic = _gen_espec_calibs(calibs, aprioris=False, heredar=True, corresp=True)

        calibrador(func_opt, paráms=sim.paráms, calibs=espec_calibs).calibrar(n_iter=n_iter, nombre=nombre)

    def guardar_calibs(símismo, directorio=''):
        for m in símismo.módulos:
            m.guardar_calibs(directorio=os.path.join(directorio, str(m)))


def _gen_reps(reps, calib=False):
    if calib:
        base = {'paráms': 15, 'estoc': 5}
    else:
        base = {'paráms': 1, 'estoc': 30}
    if reps is None:
        return base
    if isinstance(reps, int):
        return {'paráms': reps, 'estoc': reps}

    extras = {ll for ll in reps if ll not in base}
    if extras:
        raise ValueError('{extras} no es valor aceptable para eje de repetición.'.format(extras=', '.join(extras)))
    base.update(reps)
    return base
