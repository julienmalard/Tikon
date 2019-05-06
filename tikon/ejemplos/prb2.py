import os
from pprint import pprint

from tikon.ejemplos.prb import Oarenosella, red, exper_A
from tikon.estruc.simulador import Simulador, EspecCalibsCorrida
from tikon.exper import Exper
from tikon.rae import ObsPobs

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

red.cargar_calib(os.path.join(dir_base, 'calibs Sitio A epm ens/red'))
exper_A.cargar_calib(os.path.join(dir_base, 'calibs Sitio A epm ens'))

print('Validando sitio A...')
res_A = simul.simular(exper=exper_A)
pprint(res_A.validar())
res_A.graficar('valid sitio A')

# res_B = simul.simular(exper=exper_B)
# pprint(res_B.validar())
# res_B.graficar('valid sitio B antes calib')

simul.calibrar('Sitio B', días=100, exper=exper_B, paráms=exper_B, método='fscabc')
exper_B.guardar_calib('calibs Sitio B')

res = simul.simular(exper=exper_B)
pprint(res.validar())
res.graficar('valid sitio B')
