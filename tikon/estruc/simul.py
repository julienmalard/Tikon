import os
import threading

from tikon.exper import Exper

from .tiempo import Tiempo

class PlantillaSimul(object):

    def __init__(símismo, nombre, subsimuls):
        símismo.nombre = nombre
        símismo._subsimuls = {str(s): s for s in subsimuls}

    def iniciar_estruc(símismo):
        for s in símismo:
            símismo[s].iniciar_estruc()

    def iniciar_vals(símismo):
        for s in símismo:
            símismo[s].iniciar_vals()

    def incrementar(símismo, paso):
        for s in símismo:
            símismo[s].incrementar(paso)

    def cerrar(símismo):
        for s in símismo:
            símismo[s].cerrar()

    def verificar_estado(símismo):
        for s in símismo:
            símismo[s].verificar_estado()

    def reps_necesarias(símismo, frac_incert=0.95, confianza=0.95):
        return {s: símismo[s].reps_necesarias(frac_incert, confianza) for s in símismo}

    def validar(símismo, proc=None):
        valid = {s: símismo[s].validar(proc=proc) for s in símismo}
        return {ll: v for ll, v in valid.items() if v}

    def procesar_calib(símismo, proc):
        vals, pesos = zip(*[s.procesar_calib(proc) for s in símismo])
        nombre = símismo.__class__.__name__
        return proc.f_vals[nombre](vals, pesos=pesos), proc.f_pesos[nombre](pesos)

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
    def __init__(símismo, módulos, exper, t, reps):
        símismo.reps = gen_reps(reps)

        exper = [exper] if isinstance(exper, Exper) else exper
        super().__init__([SimulExper(módulos, exper=exp, t=t) for exp in exper])

    def simular(símismo):
        símismo.iniciar()
        símismo.correr()
        símismo.cerrar()

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

    def iniciar(símismo):
        símismo.iniciar_estruc()
        símismo.iniciar_vals()


class SimulExper(PlantillaSimul):
    def __init__(símismo, módulos, exper, t):
        símismo.exper = exper
        símismo.t =
        super().__init__([m.gen_simul(símismo) for m in módulos])

    def correr(símismo):
        while símismo.t.avanzar():
            símismo.incrementar(símismo.t.paso)

    def iniciar_vals(símismo):
        símismo.t.reinic()

        super().iniciar_vals()

    def iniciar_estruc(símismo):
        símismo.exper.iniciar_estruc()  # para hacer: ¿necesario?
        super().iniciar_estruc()


class SimulMódulo(PlantillaSimul):
    def __init__(símismo, resultados, simul_exper):
        símismo.simul_exper = simul_exper
        super().__init__(resultados)

    def poner_valor(símismo, var, val, rel=False):
        if rel:
            símismo[var].datos += val
        else:
            símismo[var].datos = val

    def obt_valor(símismo, var):
        return símismo[var].datos

    def inter(símismo, coso, tipo):
        pass
