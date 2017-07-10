import tikon.RAE.Insecto as Ins
import tikon.RAE.Planta as Plt
from tikon.Matemáticas.Experimentos import Experimento

# Opciones artísticas
dib_aprioris = False
ops_dib = {'incert': None, 'todas_líneas': True}

# Empezamos las cosas serias ahora
proyecto = 'Café\\Leucoptera_coffeella'
Café = Plt.Hojas('Café', proyecto=proyecto)
Café.estimar_densidad(rango=(38000e6, 42000e6), certidumbre=0.95)

Leucoptera_coffeella = Experimento(nombre='Suconusco_Chiapas', proyecto=proyecto)
Leucoptera_coffeella.agregar_orgs(archivo='Suconusco_Chiapas.csv', col_tiempo='Dia', factor=1)

Leucoptera_coffeella = Ins.MetamCompleta('L.coffeella', proyecto=proyecto, njuvenil=1)

Parasitoide_larvas = Ins.Parasitoide('Parasitoide larvas', proyecto=proyecto)

Parasitoides_pupa = Ins.Parasitoide('Parasitoide pupas', proyecto=proyecto)

Leucoptera_coffeella.secome(Café, etps_depred='juvenil')