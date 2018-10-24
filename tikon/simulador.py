from typing import Dict
import math as mat

from tikon.experimentos import Exper
from .módulo import Módulo


class Simulador(object):

    def __init__(símismo):
        símismo.módulos = {}  # type: Dict[str, Módulo]
        símismo.exper = Exper()

    def simular(
            símismo, días=None, f_inic=None, paso=1, exper=None, nombre=None, calibs=None, n_rep_estoc=30, n_rep_parám=30
    ):

        n_pasos = mat.ceil(días / paso)

        símismo.iniciar(días, f_inic, paso, n_rep_estoc, n_rep_parám)
        símismo.correr(paso, n_pasos)
        símismo.cerrar()

    def iniciar(símismo, días, f_inic, paso, n_rep_estoc, n_rep_parám):

        for m in símismo.módulos.values():
            m._iniciar(días, f_inic, paso, n_rep_estoc, n_rep_parám)

    def correr(símismo, paso, n_pasos):

        for _ in range(n_pasos):
            símismo.incrementar(paso)

    def incrementar(símismo, paso):
        for m in símismo.módulos.values():
            m._incrementar(paso)

    def cerrar(símismo):
        for m in símismo.módulos.values():
            m._cerrar()

    def calibrar(símismo, nombre=None, exper=None, n_iter=300, método='epm', paso=1, n_rep_estoc=30):




