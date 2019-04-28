import itertools
import os
from copy import deepcopy
from multiprocessing import Pool as Reserva
from pprint import pprint

from tikon.ejemplos.prb import red, exper_A
from tikon.estruc.simulador import Simulador

simul = Simulador(red)

métodos = ['mc', 'epm', 'mhl', 'cmmc', 'caa', 'fscabc', 'maed', 'as', 'sceua', 'erp']
f_objs = ['ens', 'ekg', 'rcep', 'corresp', 'r2', 'rcnep']
borrar = False


def _calibrar(*args):
    m, f = args[0]
    s = deepcopy(simul)
    exp = deepcopy(exper_A)
    nombre = f'{m}_{f} pupa'
    arch_calib = f'calibs {nombre}'

    if borrar or not os.path.isdir(arch_calib):
        print(f'Calibrando {nombre}')
        s.calibrar(nombre, exper=exp, método=m, f=f)
        s.guardar_calib(arch_calib)
        exp.guardar_calib(arch_calib)

        print(f'Validando {nombre}')
        res = s.simular(exper=exp)
        pprint(res.validar())
        print(f'Dibujando {nombre}')
        res.graficar(f'valid {nombre}')
    else:
        print(f'Saltando {nombre}')


if __name__ == '__main__':
    with Reserva() as r:
        res_paralelo = r.map(_calibrar, itertools.product(métodos, f_objs))
