from tikon.central.exper import Exper
from tikon.ejemplos.datos import obt_datos
from tikon.móds.rae import MetamCompleta, Parasitoide
from tikon.móds.rae import ObsPobs
from tikon.móds.rae import RedAE

# Mariposas tienen metamórfosis completa
Oarenosella = MetamCompleta('O. arenosella', njuvenil=5)

# 2 tipos de parasitoides
Paras_larvas = Parasitoide('Parasitoide larvas', pupa=True)
Paras_pupa = Parasitoide('Parasitoide pupa')

# El parasitoide de larvas parasita las fases 3, 4, y 5 de O. arenosela y emergen después de la quinta
Paras_larvas.parasita(Oarenosella, ['juvenil_3', 'juvenil_4', 'juvenil_5'], etp_emerg='juvenil_5')

# El parasitoide de pupas parasita y emerge de la pupa
Paras_pupa.parasita(Oarenosella, 'pupa', etp_emerg='pupa')

# Juntamos todo en una red
red = RedAE([Oarenosella, Paras_larvas, Paras_pupa])

# Datos de observaciones
datos = obt_datos('Perera et al 1988/Oarenosella_A.csv')

# Se trata de observaciones de poblaciones (y no de otro variable, como depredación).
pobs = ObsPobs.de_csv(
    datos,
    tiempo='Día',
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
    factor=655757.1429 / 500  # para convertir a individuos por ha
)

exper_A = Exper('Sitio A', pobs)
