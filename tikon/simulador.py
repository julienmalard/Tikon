import math as mat

from tikon.calib import gen_calibrador
from tikon.experimentos import Exper
from tikon.rsltd.valid import Validación


class Simulador(object):

    def __init__(símismo, módulos):
        símismo.módulos = MnjdrMódulos(módulos)
        símismo.exper = Exper()

    def simular(
            símismo, días=None, f_inic=None, paso=1, exper=None, calibs=None, n_rep_estoc=30, n_rep_parám=30
    ):

        exper = exper or símismo.exper
        días = días or exper.días()
        f_inic = f_inic or exper.f_inic()

        n_pasos = mat.ceil(días / paso)

        símismo.iniciar(días, f_inic, paso, n_rep_estoc, n_rep_parám)
        símismo.correr(paso, n_pasos)
        símismo.cerrar()

    def iniciar(símismo, días, f_inic, paso, n_rep_estoc, n_rep_parám):

        for m in símismo.módulos:
            m.iniciar(días, f_inic, paso, n_rep_estoc, n_rep_parám)

    def correr(símismo, paso, n_pasos):

        for _ in range(n_pasos):
            símismo.incrementar(paso)

    def incrementar(símismo, paso):
        for m in símismo.módulos:
            m.incrementar(paso)

    def cerrar(símismo):
        for m in símismo.módulos:
            m.cerrar()

    def validar(símismo, exper=None, paso=1, calibs=None, n_rep_estoc=30, n_rep_parám=30):

        símismo.simular(paso=paso, exper=exper, calibs=calibs, n_rep_estoc=n_rep_estoc, n_rep_parám=n_rep_parám)

        return Validación(símismo.módulos)

    def calibrar(símismo, exper=None, n_iter=300, método='epm', paso=1, n_rep_estoc=30):

        tipo_clbrd = gen_calibrador(método)

        símismo.iniciar(paso=paso, n_rep_estoc=n_rep_estoc, n_rep_parám=1)

        func = símismo._func_calib()
        clbrd = tipo_clbrd(func)

        clbrd.calibrar(n_iter=n_iter, método=método)

    def _func_calib(símismo, paso):



class MnjdrMódulos(object):
    def __init__(símismo, módulos):
        símismo.módulos = {}

    def obt_valor(símismo, mód, var):
        return símismo[mód].

    def __iter__(símismo):
        for m in símismo.módulos.values():
            yield m

    def __getitem__(símismo, itema):
        return símismo.módulos[itema]
