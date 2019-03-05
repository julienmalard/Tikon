import os
from pprint import pprint

from tikon.ejemplos.prb import red, Paras_pupa, exper_A, Paras_larvas
from tikon.estruc.simulador import Simulador
from tikon.manejo.acciones import AgregarPob
from tikon.manejo.conds import CondTiempo
from tikon.manejo.manejo import Manejo, Regla

simul = Simulador(red)

dir_base = os.path.split(__file__)[0]
red.cargar_calib(os.path.join(dir_base, 'calibs Sitio A fscabc', 'red'))
exper_A.cargar_calib(os.path.join(dir_base, 'calibs Sitio A fscabc'))

# res = simul.simular(exper=exper_A, n_rep_estoc=15, n_rep_parám=15)
# pprint(res.validar())
# res.graficar('sin biocontrol')

biocontrol = Regla(CondTiempo(1), AgregarPob(Paras_larvas['adulto'], 2e10))
manejo = Manejo(biocontrol)
simul2 = Simulador([red, manejo])

res2 = simul2.simular(exper=exper_A, n_rep_estoc=15, n_rep_parám=15)
res2.graficar('con biocontrol')
