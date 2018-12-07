from tikon.calib import gen_calibrador
from tikon.clima import Clima
from tikon.exper import Exper
from tikon.manejo import Manejo
from tikon.rsltd.valid import Validación
from tikon.tiempo import Tiempo


class Simulador(object):

    def __init__(símismo, módulos):
        símismo._módulos = módulos
        símismo.mnjdr_móds = None  # type: MnjdrMódulos
        símismo.exper = None  # type: Exper
        símismo.tiempo = None  # type: Tiempo
        símismo.corrida = None  # type: ResultadosSimul

    def simular(símismo, días=None, f_inic=None, paso=1, exper=None, calibs=None, n_rep_estoc=30, n_rep_parám=30):

        símismo.iniciar(días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám)
        símismo.correr()
        símismo.cerrar()

        return símismo.corrida

    def iniciar(símismo, días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám):

        símismo.iniciar_estruc(días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám)
        símismo.iniciar_vals()

    def iniciar_estruc(símismo, días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám):

        símismo.exper = exper or Exper()
        símismo.mnjdr_móds = MnjdrMódulos(símismo._módulos, símismo.exper)

        n_días = días or símismo.exper.días()
        f_inic = f_inic or símismo.exper.f_inic()

        símismo.tiempo = Tiempo(día=0, f_inic=f_inic, paso=paso, n_días=n_días)
        parc = símismo.mnjdr_móds.obt_val_control('parcelas')

        for m in símismo.mnjdr_móds:
            m.iniciar_estruc(símismo.tiempo, símismo.mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc)

    def iniciar_vals(símismo):

        símismo.corrida = ResultadosSimul(símismo.mnjdr_móds, símismo.tiempo)
        for m in símismo.mnjdr_móds:
            m.iniciar_vals()

    def correr(símismo):

        while símismo.tiempo.avanzar():
            símismo.incrementar()
            símismo.corrida.actualizar()

    def incrementar(símismo):
        for m in símismo.mnjdr_móds:
            m.incrementar()

        símismo.corrida.actualizar_res()

    def cerrar(símismo):
        for m in símismo.mnjdr_móds:
            m.cerrar()

    def validar(símismo, exper=None, paso=1, calibs=None, n_rep_estoc=30, n_rep_parám=30):

        símismo.simular(paso=paso, exper=exper, calibs=calibs, n_rep_estoc=n_rep_estoc, n_rep_parám=n_rep_parám)

        return Validación(símismo.corrida)

    def calibrar(símismo, exper=None, n_iter=300, método='epm', paso=1, n_rep_estoc=30):

        def func():
            símismo.iniciar_vals()
            símismo.correr()
            return símismo.corrida.procesar_calib()

        clbrd = gen_calibrador(método)(método, func, símismo.mnjdr_móds.paráms())

        símismo.iniciar_estruc(
            días=None, f_inic=None, paso=paso, exper=exper, calibs=None, n_rep_estoc=n_rep_estoc, n_rep_parám=1
        )

        clbrd.calibrar(func, n_iter=n_iter)


class MnjdrMódulos(object):
    def __init__(símismo, módulos, exper):
        if not isinstance(módulos, list):
            módulos = [módulos]
        módulos.extend([Manejo(), Clima()])

        símismo.módulos = {str(mód): mód for mód in módulos}
        símismo.exper  = exper

    def obt_valor(símismo, var, mód):
        return símismo[str(mód)].obt_valor(var)

    def obt_val_control(símismo, var):
        return símismo.exper.obt_control(var)

    def paráms(símismo):
        return [pr for mód in símismo for pr in mód.paráms()]

    def __iter__(símismo):
        for m in símismo.módulos.values():
            yield m

    def __getitem__(símismo, itema):
        return símismo.módulos[itema]


class ResultadosSimul(object):
    def __init__(símismo, resultados, tiempo):
        símismo.resultados
        símismo.tiempo = tiempo

        símismo.datos = NotImplemented

    def reinic(símismo):
        pass

    def actualizar(símismo):
        pass

    def procesar_calib(símismo):
        pass
