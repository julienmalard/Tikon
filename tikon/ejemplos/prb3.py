from pprint import pprint

from tikon.ejemplos import en_ejemplos
from tikon.ejemplos.prb import red, Paras_pupa, exper_A, Paras_larvas
from tikon.estruc.simulador import Simulador
from tikon.manejo.acciones import AgregarPob, MultPob
from tikon.manejo.conds import CondTiempo
from tikon.manejo.manejo import Manejo, Regla

red.cargar_calib(en_ejemplos('calibs Sitio A epm ens final/red'))
exper_A.cargar_calib(en_ejemplos('calibs Sitio A epm ens final'))

t = 50

manejo_pesticida_excepto_pupa = Manejo(
    Regla(CondTiempo(t), [MultPob(e, 0.05) for o in red for e in o if e.nombre != 'pupa'])
)
res1 = Simulador([red, manejo_pesticida_excepto_pupa]).simular(días=600, exper=exper_A, vars_interés=True)
res1.graficar('epm/con pesticida sin pupas 95%')

manejo_pesticida_adultos = Manejo(
    Regla(CondTiempo(t), [MultPob(e, 0.05) for o in red for e in o if e.nombre == 'adulto'])
)
res1 = Simulador([red, manejo_pesticida_adultos]).simular(días=600, exper=exper_A, vars_interés=True)
res1.graficar('epm/con pesticida adultos 95%')

manejo_pesticida_excepto_huevos = Manejo(
    Regla(CondTiempo(t), [MultPob(e, 0.05) for o in red for e in o if e.nombre != 'huevo'])
)
res1 = Simulador([red, manejo_pesticida_excepto_huevos]).simular(días=600, exper=exper_A, vars_interés=True)
res1.graficar('epm/con pesticida sin huevos 95%')

manejo_pesticida_todo = Manejo(
    Regla(CondTiempo(t), [MultPob(e, 0.05) for o in red for e in o])
)
res1 = Simulador([red, manejo_pesticida_todo]).simular(días=600, exper=exper_A, vars_interés=True)
res1.graficar('epm/con pesticida 95%')

biocontrol_larva = Regla(CondTiempo(40), AgregarPob(Paras_larvas['adulto'], 700000))

manejo_larva = Manejo(biocontrol_larva)

res2 = Simulador([red, manejo_larva]).simular(días=600, exper=exper_A, vars_interés=True)
res2.graficar('epm/con biocontrol larva')

biocontrol_pupa = Regla(CondTiempo(50), AgregarPob(Paras_pupa['adulto'], 700000))

manejo_pupa = Manejo(biocontrol_pupa)

res2 = Simulador([red, manejo_pupa]).simular(días=600, exper=exper_A, vars_interés=True)
res2.graficar('epm/con biocontrol pupa')

res = Simulador(red).simular(días=600, exper=exper_A, vars_interés=True)
res.graficar('epm/sin biocontrol')
pprint(res.validar())
