import os
from pprint import pprint

from tikon.ejemplos.a_prioris import a_prioris
# from tikon.ecs.aprioris import APrioriDens
from tikon.estruc.modelo import Simulador
from tikon.exper.exper import Exper
from tikon.móds.rae import MetamCompleta, Sencillo, Parasitoide
# from tikon.rae.orgs.plantas import Hojas
from tikon.móds.rae import RedAE
from tikon.móds.rae import ObsPobs

# Coco = Hojas(nombre='Palma de coco')  # Unidades: mm2 / ha
# apriori = APrioriDens(rango=(38, 42), certidumbre=0.95)
# Coco.estim_dens(apriori)

Oarenosella = MetamCompleta('O. arenosella', njuvenil=5)
Paras_larvas = Parasitoide('Parasitoide larvas', pupa=True)
Paras_pupa = Parasitoide('Parasitoide pupa')

# Oarenosella.secome(Coco, etps_símismo='juvenil')

Paras_larvas.parasita(Oarenosella, ['juvenil_3', 'juvenil_4', 'juvenil_5'], etp_emerg='juvenil_5')
Paras_pupa.parasita(Oarenosella, 'pupa', etp_emerg='pupa')

Araña = Sencillo('Araña')
Araña.secome(Oarenosella)

red = RedAE([Oarenosella, Paras_larvas, Paras_pupa])

# A prioris para la nueva red
red.espec_aprioris(a_prioris)

# Datos de observaciones
dir_base = os.path.split(__file__)[0]
pobs = ObsPobs.de_csv(
    os.path.join(dir_base, 'Oarenosella_A.csv'),
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
    },
    factor=655757.1429 / 500
)
exper_A = Exper('Sitio A', pobs)

simul = Simulador(red)

if __name__ == '__main__':
    método = 'epm'
    f = 'ens'
    post = 'k2 rep 2'
    print(post)
    # calibs = EspecCalibsCorrida(aprioris=True)
    # res = simul.simular(días=None, exper=exper_A, n_rep_parám=30, n_rep_estoc=30, calibs=calibs, vars_interés=True)
    # pprint(res.validar())
    # res.graficar('antes calibrador')
    simul.calibrar('Sitio A', método=método, f=f, exper=exper_A)
    simul.guardar_calibs(f'calibs Sitio A {método} {f}_{post}')
    exper_A.guardar_calib(f'calibs Sitio A {método} {f}_{post}')

    res2 = simul.simular(exper=exper_A, vars_interés=True)
    pprint(res2.validar())
    res2.graficar(f'con calib {método} {f}_{post}')

    # pprint(res.reps_necesarias(0.9, 0.9))
