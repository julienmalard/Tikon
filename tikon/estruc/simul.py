import os
import threading

from tikon.exper import Exper
from tikon.result.utils import gen_coords_base


class PlantillaSimul(object):

    def __init__(símismo, nombre, subsimuls):
        símismo.nombre = nombre
        símismo._subsimuls = {str(s): s for s in subsimuls}

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

    def __getitem__(símismo, itema):
        return símismo._subsimuls[str(itema)]

    def __iter__(símismo):
        for s in símismo._subsimuls:
            yield s

    def __str__(símismo):
        return símismo.nombre


class Simulación(PlantillaSimul):
    def __init__(símismo, nombre, módulos, exper, t, calibs, reps, vars_interés):

        exper = [exper] if isinstance(exper, Exper) else exper

        símismo.ecs = {m: m.gen_ecs(n_reps=reps['paráms']) for m in módulos}
        símismo.paráms = símismo.gen_paráms()

        super().__init__(
            nombre,
            subsimuls=[
                SimulExper(módulos, exper=exp, t=t, ecs=símismo.ecs, vars_interés=vars_interés) for exp in exper
            ]
        )
        calibs.llenar_vals(símismo.paráms, n_reps=reps['paráms'])

    def simular(símismo):
        símismo.iniciar()
        símismo.correr()
        símismo.cerrar()

    def iniciar(símismo):
        for ecs in símismo.ecs.values():
            ecs.act_coefs()

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
    def __init__(símismo, módulos, exper, t, ecs, vars_interés):
        símismo.exper = exper
        símismo.t = exper.gen_t(t)
        símismo.ecs = ecs
        super().__init__(
            nombre=exper.nombre,
            subsimuls=[m.gen_simul(símismo, vars_interés=vars_interés, ecs=símismo.ecs[m]) for m in módulos]
        )

        símismo.verificar_reqs()

    def verificar_reqs(símismo):

        for mód in símismo:
            for req in mód.requísitos():
                mód_req, var_req = req.split('.')
                try:
                    otro_mód = símismo[mód_req]
                except KeyError:
                    raise ValueError(
                        'Módulo {otro} requerido por módulo {mód} no existe.'.format(otro=mód_req, mód=mód)
                    )
                if var_req not in otro_mód.variables:
                    raise ValueError(
                        'Variable {var} de módulo {otro} requerido por módulo {mód} no existe.'.format(
                            var=var_req, otro=otro_mód, mód=mód
                        )
                    )
            for req in mód.requísitos(controles=True):
                if req not in símismo.exper.controles:
                    raise ValueError(
                        'Falta requísito {req} de módulo {mód} en experimento {exp}'.format(
                            req=req, mód=mód, exp=símismo.exper
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

    def __init__(símismo, nombre, simul_exper, ecs, vars_interés):
        símismo.simul_exper = simul_exper
        símismo.ecs = ecs

        coords_base = gen_coords_base(
            n_rep_estoc=simul_exper.reps['estoc'], n_rep_paráms=simul_exper.reps['paráms'],
            parc=simul_exper.exper.controles['parcelas']
        )
        objs_res = [res(sim=símismo, coords=coords_base, vars_interés=vars_interés) for res in símismo.resultados]
        super().__init__(nombre, objs_res)

    def gen_paráms(símismo):
        return símismo.ecs.vals_paráms()

    def incrementar(símismo, paso, f):
        if símismo.ecs:
            símismo.ecs.eval(paso=paso, sim=símismo)

    def poner_valor(símismo, var, val, rel=False):
        if rel:
            símismo[var].datos += val
        else:
            símismo[var].datos = val

    def obt_valor(símismo, var):
        return símismo[var].datos

    def inter(símismo, coso, tipo):
        pass