import os
import threading

from tikon.central.errores import ErrorRequísitos, ErrorNombreInválido
from tikon.central.exper import Exper
from tikon.central.utils import gen_coords_base
from tikon.result.proc import ens
from tikon.result.valid import Valid, gen_proc_valid


class PlantillaSimul(object):

    def __init__(símismo, nombre, subs):
        símismo.nombre = nombre
        símismo._subs = {str(s): s for s in subs}

    def iniciar(símismo):
        for s in símismo:
            símismo[s].iniciar()

    def incrementar(símismo, paso, f):
        for s in símismo:
            símismo[s].incrementar(paso, f)

    def cerrar(símismo):
        for s in símismo:
            símismo[s].cerrar()

    def vals_paráms(símismo):
        return _únicos([prm for s in símismo for prm in símismo[s].vals_paráms()])

    def verificar_estado(símismo):
        for s in símismo:
            símismo[s].verificar_estado()

    def validar(símismo, proc):
        return Valid({s: símismo[s].validar(proc=proc) for s in símismo}, proc=proc)

    def procesar_calib(símismo, proc):
        vals, pesos = zip(*[s.procesar_calib(proc) for s in símismo])
        return proc.f_combin(vals, pesos=pesos), proc.f_combin_pesos(pesos)

    def graficar(símismo, directorio):
        for s in símismo:
            símismo[s].graficar(directorio=os.path.join(directorio, s))

    def a_dic(símismo):
        return {s: símismo[s].a_dic() for s in símismo}

    def __contains__(símismo, itema):
        return str(itema) in símismo._subs

    def __getitem__(símismo, itema):
        return símismo._subs[str(itema)]

    def __iter__(símismo):
        for s in símismo._subs:
            yield s

    def __str__(símismo):
        return símismo.nombre


class Simulación(PlantillaSimul):
    def __init__(símismo, nombre, modelo, exper, t, calibs, reps, vars_interés):

        exper = [exper] if isinstance(exper, Exper) else exper

        símismo.ecs = {m: m.gen_ecs(modelo, mód=m, n_reps=reps['paráms']) for m in modelo.módulos}

        super().__init__(
            nombre,
            subs=[
                SimulExper(modelo.módulos, exper=exp, t=t, reps=reps, ecs=símismo.ecs, vars_interés=vars_interés)
                for exp in exper
            ]
        )

        símismo.paráms = símismo.vals_paráms()
        calibs.llenar_vals(símismo.paráms, n_reps=reps['paráms'])

    def simular(símismo):
        símismo.iniciar()
        símismo.correr()
        símismo.cerrar()

    def iniciar(símismo):
        for ecs in símismo.ecs.values():
            if ecs:
                ecs.act_vals()

        super().iniciar()

    def correr(símismo):

        # Un diccionario para comunicar errores
        errores = []

        def correr_exp(exp):
            try:
                exp.correr()
            except BaseException:
                errores.append(str(exp))
                raise

        # Un hilo para cada módulo
        l_hilo = [
            threading.Thread(name='hilo_%s' % exp, target=correr_exp, args=(símismo[exp],))
            for exp in símismo
        ]

        for hilo in l_hilo:
            hilo.start()
        for hilo in l_hilo:
            hilo.join()

        # Verificar si hubo error
        if errores:
            raise ChildProcessError('Hubo error en los módulos siguientes: {móds}'.format(móds=', '.join(errores)))

    def validar(símismo, proc=ens):
        proc = gen_proc_valid(proc)
        return super().validar(proc=proc)

    def procesar_calib(símismo, proc):
        return super().procesar_calib(proc)[0]


class SimulExper(PlantillaSimul):
    def __init__(símismo, módulos, exper, t, reps, ecs, vars_interés):
        símismo.exper = exper
        símismo.t = exper.gen_t(t)
        símismo.ecs = ecs
        símismo.reps = reps
        super().__init__(
            nombre=exper.nombre,
            subs=[m.gen_simul(símismo, vars_interés=vars_interés, ecs=símismo.ecs[m]) for m in módulos]
        )

        símismo.verificar_reqs()
        símismo.paráms_exper = símismo.exper.gen_paráms(símismo)

    def vals_paráms(símismo):
        return super().vals_paráms() + símismo.paráms_exper.vals_paráms()

    def verificar_reqs(símismo):

        for sim_mód in símismo:
            reqs_mód = símismo[sim_mód].requísitos() or []
            for req in reqs_mód:
                mód_req, var_req = req.split('.')
                try:
                    otro_mód = símismo[mód_req]
                except KeyError:
                    raise ErrorRequísitos(
                        'Módulo "{otro}" requerido por módulo "{mód}" no existe.'.format(otro=mód_req, mód=sim_mód)
                    )
                if var_req not in otro_mód:
                    raise ErrorRequísitos(
                        'Variable "{var}" de módulo "{otro}" requerido por módulo "{mód}" no existe.'.format(
                            var=var_req, otro=otro_mód, mód=sim_mód
                        )
                    )
            reqs_mód_cntrl = símismo[sim_mód].requísitos(controles=True) or []
            for req in reqs_mód_cntrl:
                if req not in símismo.exper.controles:
                    raise ErrorRequísitos(
                        'Falta requísito "{req}" de módulo "{mód}" en experimento "{exp}"'.format(
                            req=req, mód=sim_mód, exp=símismo.exper
                        )
                    )

    def iniciar(símismo):
        símismo.t.reinic()
        símismo.paráms_exper.iniciar()
        super().iniciar()

    def correr(símismo):
        for f in símismo.t.avanzar():
            símismo.incrementar(símismo.t.paso, f)


class SimulMódulo(PlantillaSimul):
    resultados = []

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        if '.' in mód.nombre:
            raise ErrorNombreInválido(
                'Nombre {nombre} inválido: Nombres de módulos no pueden contener ".".'.format(nombre=mód.nombre)
            )

        símismo.simul_exper = simul_exper
        símismo.exper = simul_exper.exper
        símismo.ecs = ecs
        símismo.mód = mód

        coords_base = gen_coords_base(
            n_rep_estoc=simul_exper.reps['estoc'], n_rep_paráms=simul_exper.reps['paráms'],
            parc=simul_exper.exper.controles['parcelas']
        )
        símismo.nombre = mód.nombre
        objs_res = [res(sim=símismo, coords=coords_base, vars_interés=vars_interés) for res in símismo.resultados]
        super().__init__(mód.nombre, objs_res)

    def vals_paráms(símismo):
        return símismo.ecs.vals_paráms() if símismo.ecs else []

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        if símismo.ecs:
            símismo.ecs.eval(paso=paso, sim=símismo)

    def obt_valor(símismo, var):
        return símismo[var].datos

    def obt_valor_extern(símismo, var, mód=None):
        if not mód:
            mód, var = var.split('.')

        return símismo.simul_exper[mód].obt_valor(var)

    def obt_valor_control(símismo, var):
        return símismo.exper.controles[var]

    def poner_valor(símismo, var, val, rel=False):
        if rel:
            símismo[var].datos += val
        else:
            símismo[var].datos = val

    def poner_valor_extern(símismo, var, val, mód=None, rel=False):
        if not mód:
            mód, var = var.split('.')
        return símismo.simul_exper[mód].poner_valor(var, val, rel=rel)

    def requísitos(símismo, controles=False):
        if símismo.ecs:
            return símismo.ecs.requísitos(controles=controles)


def _únicos(lista):
    final = []
    for l in lista:
        if l not in final:
            final.append(l)
    return final
