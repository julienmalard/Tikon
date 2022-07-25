from tikon.central import Parcela, Modelo, GeomParcela
from tikon.central.exper import Exper
from tikon.ejemplos.datos import obt_datos
from tikon.móds.rae.orgs.insectos import MetamCompleta, Parasitoide
from tikon.móds.rae.red import RedAE, ObsPobs

# Mariposas tienen metamorfosis completa
Oarenosella = MetamCompleta('O. arenosella', njuvenil=5)

# 2 tipos de parasitoides
Paras_larvas = Parasitoide('Parasitoide larvas', pupa=True)
Paras_pupa = Parasitoide('Parasitoide pupa')

# Juntamos todo en una red
RedOArenosella = RedAE([Oarenosella, Paras_larvas, Paras_pupa])

with RedOArenosella:
    # El parasitoide de larvas parasita las fases 3, 4, y 5 de O. arenosela y emergen después de la quinta
    Paras_larvas.parasita(Oarenosella, ['juvenil 3', 'juvenil 4', 'juvenil 5'], etp_emerg='juvenil 5')

    # El parasitoide de pupas parasita y emerge de la pupa
    Paras_pupa.parasita(Oarenosella, 'pupa', etp_emerg='pupa')

# Datos de observaciones
datos = obt_datos('Perera et al 1988/Oarenosella_A.csv')

# Se trata de observaciones de poblaciones (y no de otro variable, como depredación).
pobs = ObsPobs.de_cuadro(
    datos,
    tiempo='Día',
    corresp={
        'Estado 1': Oarenosella['juvenil 1'],
        'Estado 2': Oarenosella['juvenil 2'],
        'Estado 3': Oarenosella['juvenil 3'],
        'Estado 4': Oarenosella['juvenil 4'],
        'Estado 5': Oarenosella['juvenil 5'],
        'Pupa': Oarenosella['pupa'],
        'Para_larva_abs': Paras_larvas['juvenil'],
        'Para_pupa_abs': Paras_pupa['juvenil']
    },
    factor=655757.1429 / 500  # para convertir a individuos por ha
)

exper_A = Exper('Sitio A', Parcela('Sitio A', geom=GeomParcela((7.297, 79.865))))
exper_A.datos.agregar_obs(pobs)

ModeloOArenosella = Modelo(RedOArenosella)
