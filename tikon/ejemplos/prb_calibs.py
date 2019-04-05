from pprint import pprint

from tikon.ejemplos.prb import exper_A, simul
from tikon.estruc.simulador import EspecCalibsCorrida

métodos = ['cmmc', 'epm', 'mc', 'mhl', 'as', 'sceua', 'erp', 'caa', 'fscabc']
calibs = EspecCalibsCorrida(aprioris=True)

for m in métodos:
    simul.calibrar('Sitio A', días=None, método=m, exper=exper_A, n_iter=5)
    simul.guardar_calib('calibs Sitio A ' + m)
    exper_A.guardar_calib('calibs Sitio A ' + m)

    res2 = simul.simular(días=None, exper=exper_A, n_rep_parám=30, n_rep_estoc=30, vars_interés=True)
    pprint(res2.validar())
    res2.graficar('con calib ' + m)
