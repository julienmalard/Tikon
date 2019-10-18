from tikon.exper import Exper
from tikon.result.res import ResultadosSimul

from .tiempo import Tiempo


class Simulación(object):
    def __init__(símismo, módulos, exper, t, reps):

        símismo.reps = gen_reps(reps)

        símismo.exper = [exper] if isinstance(exper, Exper) else exper
        símismo.módulos = módulos
        símismo.t = t if isinstance(t, Tiempo) else Tiempo(t)
        símismo.res = ResultadosSimul(símismo)

    def simular(símismo):
        símismo.iniciar()
        símismo.correr()
        símismo.cerrar()

        return símismo.res

    def iniciar(símismo):
        símismo.iniciar_estruc()
        símismo.iniciar_vals()

    def iniciar_estruc(símismo):
        for m in símismo.módulos:
            m.iniciar_estruc()

        for e in símismo.exper:
            e.iniciar_estruc()

    def iniciar_vals(símismo):
        símismo.res.reinic()

        for m in símismo.módulos:
            m.iniciar_vals()

    def correr(símismo):
        while símismo.t.avanzar():
            símismo.incrementar()

    def incrementar(símismo):
        for m in símismo.módulos:
            m.incrementar()

        símismo.res.actualizar()

    def cerrar(símismo):
        símismo.res.finalizar()

        for m in símismo.módulos:
            m.cerrar()
