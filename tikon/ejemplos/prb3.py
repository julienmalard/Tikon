from tikon.ejemplos.prb import red, Paras_pupa, exper_A, Paras_larvas
from tikon.estruc.simulador import Simulador
from tikon.manejo.acciones import AgregarPob
from tikon.manejo.conds import CondTiempo, CondCada
from tikon.manejo.manejo import Manejo, Regla
from tikon.ejemplos import en_ejemplos

simul = Simulador(red)

red.cargar_calib(en_ejemplos('calibs Sitio A epm/red'))
exper_A.cargar_calib(en_ejemplos('calibs Sitio A epm'))

res = simul.simular(exper=exper_A, n_rep_estoc=15, n_rep_parám=15, vars_interés=True)
res.graficar('epm/sin biocontrol')

biocontrol = Regla(CondCada(10), AgregarPob(Paras_pupa['adulto'], 2e10))

manejo = Manejo(biocontrol)
simul2 = Simulador([red, manejo])

res2 = simul2.simular(exper=exper_A, n_rep_estoc=15, n_rep_parám=15, vars_interés=True)
res2.graficar('epm/con biocontrol')
