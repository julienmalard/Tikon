import os
from pprint import pprint

from tikon.ejemplos.prb import Oarenosella, red
from tikon.estruc.simulador import Simulador
from tikon.exper.exper import Exper
from tikon.rae.red_ae.obs import ObsPobs

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
exper_B = Exper(pobs)

simul = Simulador(red)

red.cargar_calib(os.path.join(dir_base, 'calibs Sitio A fscabc/red'))

simul.calibrar('Sitio B', días=21, exper=exper_B, paráms=exper_B, método='fscabc')

res = simul.simular(exper=exper_B)
pprint(res.validar())
res.graficar('valid sitio B')
