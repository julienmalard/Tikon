from pprint import pprint

from pruebas.a_prioris import a_prioris
from tikon.estruc.simulador import Simulador, EspecCalibsCorrida
from tikon.exper.exper import Exper
from tikon.rae.orgs.insectos.gnrc import MetamCompleta, Sencillo
from tikon.rae.orgs.insectos.paras import Parasitoide
from tikon.rae.red_ae.obs import ObsPobs
from tikon.rae.red_ae.red import RedAE

Oarenosella = MetamCompleta('O. arenosella', njuvenil=5)
Paras_larvas = Parasitoide('Parasitoide larvas')
Paras_pupa = Parasitoide('Parasitoide pupa')

Paras_larvas.parasita(Oarenosella, ['juvenil_1', 'juvenil_2', 'juvenil_3'], etp_emerg='pupa')
Paras_pupa.parasita(Oarenosella, 'pupa', etp_emerg='pupa')

Araña = Sencillo('Araña')
Araña.secome(Oarenosella)

red = RedAE([Oarenosella, Paras_larvas, Paras_pupa])

# A prioris para la nueva red
red.espec_aprioris(a_prioris)

# Datos de observaciones
exper_A = Exper()
pobs = ObsPobs.de_csv(
    '/Users/julienmalard/PycharmProjects/Tikon/pruebas/Oarenosella_A.csv',
    col_tiempo='Día',
    corresp={
        'Estado 1': Oarenosella['juvenil_1'],
        'Estado 2': Oarenosella['juvenil_2'],
        'Estado 3': Oarenosella['juvenil_3'],
        'Estado 4': Oarenosella['juvenil_4'],
        'Estado 5': Oarenosella['juvenil_5'],
        'Pupa': Oarenosella['pupa'],
        'Para_larva_abs': Paras_larvas['juvenil'],
        'Para_pupa_abs': Paras_pupa['juvenil']
    }
)
exper_A.agregar_obs(pobs)

simul = Simulador(red)

calibs = EspecCalibsCorrida(aprioris=True)
res = simul.simular(50, exper=exper_A, n_rep_parám=31, n_rep_estoc=30, calibs=calibs)

pprint(res.reps_necesarias(0.9, 0.9))
print(res)
