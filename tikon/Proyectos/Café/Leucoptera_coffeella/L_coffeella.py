import tikon.RAE.Insecto as Ins
from tikon.Matemáticas.Experimentos import Experimento
from tikon.Proyectos.Café.Leucoptera_coffeella.a_prioris import a_prioris
from tikon.RAE.RedAE import Red
import tikon.RAE.Planta as Plt

# Opciones artísticas
dib_aprioris = True
ops_dib = {'incert': None, 'todas_líneas': False}

# Empezamos las cosas serias ahora
proyecto = 'Café\\Leucoptera_coffeella'

# Crear objeto planta
Café = Plt.Hojas('Café', proyecto=proyecto)
Café.estimar_densidad(rango=(38000e6, 42000e6), certidumbre=0.95)

# Crear objeto "base de datos"
El_Encanto = Experimento(nombre='Suconusco_Chiapas', proyecto=proyecto)
# Datos tomados de
#    Lomeli-Flores, J. Refugio, Juan F. Barrera, and Julio S. Bernal. 2009. “Impact of Natural Enemies on Coffee
#       Leafminer Leucoptera Coffeella (Lepidoptera: Lyonetiidae) Population Dynamics in Chiapas, Mexico.”
#       Biological Control 51 (1): 51–60. doi:10.1016/j.biocontrol.2009.03.021.
#    Lomeli-Flores, J. Refugio, Juan F. Barrera, and Julio S. Bernal. 2010. “Impacts of Weather, Shade Cover and
#       Elevation on Coffee Leafminer Leucoptera Coffeella (Lepidoptera: Lyonetiidae) Population Dynamics and
#       Natural Enemies.” Crop Protection 29 (9): 1039–48. doi:10.1016/j.cropro.2010.03.007.

El_Encanto.agregar_pobs(archivo='Suconusco_Chiapas.csv', col_tiempo='Día', factor=900 * 1000)
# Factor: datos en Suconusco_Chiapas está por larvas/plantas; se asume que hay 1 panta cada 10 m2 (2mx5m).
# El factor de 100 cambia los datos de individuos/plantas a individuos/hectarias.


# Crear objetos para los insectos de esta red
L_coffeella = Ins.MetamCompleta('L. coffeella', proyecto=proyecto, njuvenil=1)
L_coffeella.secome(Café, etps_depred='juvenil')

Parasitoide_larvas = Ins.Parasitoide('Parasitoide larvas', proyecto=proyecto)
Parasitoide_larvas.parasita(L_coffeella, etps_infec=['juvenil'], etp_sale='juvenil')


# Crear objeto red
Red_café = Red(nombre='Café', organismos=[L_coffeella, Parasitoide_larvas, Café],
               proyecto=proyecto)

Red_café.añadir_exp(El_Encanto,
                    corresp={'L. coffeella': {'juvenil': ['Juvenil']
#                                              'huevo': ['Huevo'],
#                                              'pupa': ['Pupa'],
#                                              'adulto': ['Adulto']
                                                },
                             'Parasitoide larvas': {'juvenil': ['Para_larva']}}
                    )

# A prioris para la nueva red
for org in [L_coffeella, Parasitoide_larvas]:
    try:
        for a_priori in a_prioris[org.nombre]:
            org.especificar_apriori(**a_priori)
    except KeyError:
        pass

from pprint import pprint

pprint(Red_café.ver_coefs_no_espec())
Red_café.sensibilidad(nombre='Sensib_sobol', exper=El_Encanto, n=10)

Red_café.validar(nombre='Valid antes de calib', exper=El_Encanto, n_rep_parám=10, n_rep_estoc=10)

Red_café.calibrar('Prueba', n_iter=10, quema=0, extraer=1, dibujar=True)

Red_café.validar(exper=El_Encanto, nombre='Valid prueba', n_rep_parám=10, n_rep_estoc=10)

Red_café.sensibilidad(nombre='Sensib_sobol', exper=El_Encanto, n=10)
