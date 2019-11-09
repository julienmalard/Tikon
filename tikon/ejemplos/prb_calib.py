import os
from copy import deepcopy
from multiprocessing import Pool as Reserva
from pprint import pprint

from tikon.ejemplos.prb import red, exper_A
from tikon.central.modelo import Simulador
from tikon.utils import guardar_json

simul = Simulador(red)

f_objs = ['ens', 'ekg', 'rcep', 'rcnep']  # , 'log p', 'verosimil_gaus', 'rcep', 'corresp', 'r2', 'rcnep']
borrar = False
métodos = {
    #    'mc': f_objs,
    'epm': f_objs,
    #    'bdd': ['verosimil_gaus'],
    #    'mhl': f_objs,
    #    'cmmc': ['log_p'],
    #    'caa': f_objs,
    #    'fscabc': f_objs,
    #    'maed': ['log_p'],
    #    'as': f_objs,
    #    'sceua': f_objs,
    #    'erp': f_objs,
    #    'cmed': ['log_p'],
}


def _calibrar(*args):
    m, f = args[0]
    s = deepcopy(simul)
    exp = deepcopy(exper_A)
    nombre = f'{m}_{f}'
    arch_calib = f'calibs {nombre}'

    if borrar or not os.path.isdir(arch_calib):
        print(f'Calibrando {nombre}')
        s.calibrar(nombre, n_iter=1000, exper=exp, método=m, f=f)
        s.guardar_calibs(arch_calib)
        exp.guardar_calibs(arch_calib)

        print(f'Validando {nombre}')
        res = s.simular(exper=exp)
        valid = res.validar()
        pprint(valid)
        guardar_json(valid, os.path.join(arch_calib, 'valid.json'))
        print(f'Dibujando {nombre}')
        res.graficar(f'valid {nombre}')
    else:
        print(f'Saltando {nombre}')


if __name__ == '__main__':
    with Reserva() as r:
        para_correr = [(m, f) for m in métodos for f in métodos[m]]
        res_paralelo = r.map(_calibrar, para_correr)
