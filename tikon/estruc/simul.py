import os
import threading

from tikon.result.utils import gen_coords_base

from .exper import Exper


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

    def gen_paráms(símismo):
        return set(prm for s in símismo for prm in símismo[s].gen_paráms())

    def verificar_estado(símismo):
        for s in símismo:
            símismo[s].verificar_estado()

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        return {s: símismo[s].reps_necesarias(frac_incert, confianza) for s in símismo}

    def validar(símismo, proc):
        valid = {s: símismo[s].validar(proc=proc) for s in símismo}
        return {ll: v for ll, v in valid.items() if v}

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

        símismo.ecs = {m: m.gen_ecs(modelo, n_reps=reps['paráms']) for m in modelo.módulos}

        super().__init__(
            nombre,
            subs=[
                SimulExper(modelo.módulos, exper=exp, t=t, reps=reps, ecs=símismo.ecs, vars_interés=vars_interés)
                for exp in exper
            ]
        )
        símismo.paráms = símismo.gen_paráms()
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

    def verificar_reqs(símismo):

        for sim_mód in símismo:
            reqs_mód = símismo[sim_mód].requísitos() or []
            for req in reqs_mód:
                mód_req, var_req = req.split('.')
                try:
                    otro_mód = símismo[mód_req]
                except KeyError:
                    raise ValueError(
                        'Módulo "{otro}" requerido por módulo "{mód}" no existe.'.format(otro=mód_req, mód=sim_mód)
                    )
                if var_req not in otro_mód:
                    raise ValueError(
                        'Variable "{var}" de módulo "{otro}" requerido por módulo "{mód}" no existe.'.format(
                            var=var_req, otro=otro_mód, mód=sim_mód
                        )
                    )
            reqs_mód_cntrl = símismo[sim_mód].requísitos(controles=True) or []
            for req in reqs_mód_cntrl:
                if req not in símismo.exper.controles:
                    raise ValueError(
                        'Falta requísito "{req}" de módulo "{mód}" en experimento "{exp}"'.format(
                            req=req, mód=sim_mód, exp=símismo.exper
                        )
                    )

    def iniciar(símismo):
        símismo.t.reinic()
        super().iniciar()

    def correr(símismo):
        for f in símismo.t.avanzar():
            símismo.incrementar(símismo.t.paso, f)


class SimulMódulo(PlantillaSimul):
    resultados = []

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        if '.' in mód.nombre:
            raise ValueError(
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
        objs_res = [res(sim=símismo, coords=coords_base, vars_interés=vars_interés) for res in símismo.resultados]
        super().__init__(mód.nombre, objs_res)

    def gen_paráms(símismo):
        return símismo.ecs.vals_paráms() if símismo.ecs else []

    def iniciar(símismo):
        pass

    def incrementar(símismo, paso, f):
        if símismo.ecs:
            símismo.ecs.eval(paso=paso, sim=símismo)

    def cerrar(símismo):
        pass

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
