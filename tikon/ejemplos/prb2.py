from pprint import pprint

from tikon.ejemplos.prb import red, Oarenosella, Paras_pupa, Paras_larvas, exper_A
from tikon.estruc.simulador import Simulador
from tikon.manejo.acciones import AgregarPob
from tikon.manejo.conds import CondTiempo
from tikon.manejo.manejo import Manejo, Regla

simul = Simulador(red)

dir_calibs = 'calibs Sitio A fscabc'
Oarenosella.cargar_calib(dir_calibs)
Paras_larvas.cargar_calib(dir_calibs)
Paras_pupa.cargar_calib(dir_calibs)

método = 'fscabc'
res = simul.simular(exper=exper_A)
pprint(res.validar())
res.graficar('con calib ' + método)

biocontrol = Regla(CondTiempo(20), AgregarPob(Paras_pupa['adulto'], 2e6))
manejo = Manejo(biocontrol)
simul2 = Simulador([red, manejo])

res2 = simul2.simular(exper=exper_A)
res2.graficar('con biocontrol')
