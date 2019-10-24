import os
from copy import deepcopy
from pprint import pprint

from tikon.ejemplos.prb import Oarenosella, red, exper_A
from tikon.estruc.modelo import Simulador
from tikon.exper import Exper
from tikon.móds.rae import ObsPobs

dir_base = os.path.split(__file__)[0]
pobs = ObsPobs.de_csv(
    os.path.join(dir_base, 'Oarenosella_B.csv'),
    col_tiempo='Día',
    corresp={
        'Estado 1': Oarenosella['juvenil_1'],
        'Estado 2': Oarenosella['juvenil_2'],
        'Estado 3': Oarenosella['juvenil_3'],
        'Estado 4': Oarenosella['juvenil_4'],
        'Estado 5': Oarenosella['juvenil_5'],
        'Pupa': Oarenosella['pupa'],
    },
    factor=655757.1429 / 500
)
exper_B = Exper('Sitio B', pobs)

simul = Simulador(red)
simul2 = Simulador(deepcopy(red))

copia_exper_B = deepcopy(exper_B)
simul2.calibrar('Sitio B', exper=copia_exper_B)
simul2.guardar_calibs('calibs Sitio B')
copia_exper_B.guardar_calib('calibs sitio B')
res = simul.simular(exper=copia_exper_B)
pprint(res.validar())
res.graficar('valid sitio B')

red.cargar_calib(os.path.join(dir_base, 'calibs Sitio A epm ens final/red'))
# exper_A.cargar_calib(os.path.join(dir_base, 'calibs Sitio A epm ens final'))

simul.calibrar('calibrador inic sitio A', días=100, paráms=exper_A, exper=exper_A, n_rep_parám=30)
print('Validando sitio A...')
res_A = simul.simular(exper=exper_A)
pprint(res_A.validar())
res_A.graficar('valid sitio A')

# res_B = simul.simular(exper=exper_B)
# pprint(res_B.validar())
# res_B.graficar('valid sitio B antes calibrador')

simul.calibrar('Sitio B', días=100, exper=exper_B, paráms=exper_B, método='epm', n_rep_parám=30)
exper_B.guardar_calib('calibs inic Sitio B')

res = simul.simular(exper=exper_B)
pprint(res.validar())
res.graficar('valid inic sitio B')
