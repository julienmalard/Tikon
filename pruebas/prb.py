from pprint import pprint

from pruebas.a_prioris import a_prioris
from tikon.rae.orgs.insectos.gnrc import MetamCompleta
from tikon.rae.orgs.insectos.paras import Parasitoide
from tikon.rae.red_ae.red import RedAE
from tikon.simulador import Simulador, EspecCalibsCorrida

Oarenosella = MetamCompleta('O. arenosella', njuvenil=5)
Paras_larvas = Parasitoide('Parasitoide larvas')
Paras_pupa = Parasitoide('Parasitoide pupa')

Paras_larvas.parasita(Oarenosella, ['juvenil_1', 'juvenil_2', 'juvenil_3'], etp_emerg='pupa')
Paras_pupa.parasita(Oarenosella, 'pupa', etp_emerg='pupa')

# Araña = Sencillo('Araña')
# Araña.secome(Oarenosella)

red = RedAE([Oarenosella, Paras_larvas, Paras_pupa])

# A prioris para la nueva red
red.espec_aprioris(a_prioris)

simul = Simulador(red)

calibs = EspecCalibsCorrida(aprioris=True)
res = simul.simular(50, n_rep_parám=20, n_rep_estoc=20, calibs=calibs)

pprint(res.reps_necesarias())
print(res)
