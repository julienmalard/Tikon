from pprint import pprint

from تقدیر.ذرائع import سی_اس_وی as clima_csv

from tikon.ejemplos.Leucoptera_coffeella.a_prioris import a_prioris
from tikon.móds.clima.clima import Clima
from tikon.ecs.aprioris import APrioriDens
from tikon.estruc.modelo import Simulador, EspecCalibsCorrida
from tikon.estruc.exper import Exper
from tikon.móds.rae import MetamCompleta, Parasitoide
from tikon.móds.rae.orgs.plantas import Hojas
from tikon.móds.rae import RedAE
from tikon.móds.rae import ObsPobs

# Crear objeto planta
Café = Hojas('Café')
dens = APrioriDens(rango=(38000e6, 42000e6), certidumbre=0.95)
Café.estim_dens(dens)

# Crear objetos para los insectos de esta red
L_coffeella = MetamCompleta('L. coffeella')
L_coffeella.secome(Café, etps_símismo='juvenil')

Parasitoide_larvas = Parasitoide('Parasitoide larvas')
Parasitoide_larvas.parasita(L_coffeella, etps_entra=['juvenil'], etp_emerg='juvenil')

L_coffeella.activar_ec('Edad', subcateg='Ecuación', ec='Días grados')
Parasitoide_larvas.activar_ec('Edad', subcateg='Ecuación', ec='Días grados')

# Crear objeto red
Red_café = RedAE([L_coffeella, Parasitoide_larvas, Café])

# A prioris para la nueva red
Red_café.espec_aprioris(a_prioris)

# pprint(Red_café.ver_coefs_no_espec())

# Crear objeto "base de datos"
El_Encanto = Exper()
# Datos tomados de
#    Lomeli-Flores, J. Refugio, Juan F. Barrera, and Julio S. Bernal. 2009. “Impact of Natural Enemies on Coffee
#       Leafminer Leucoptera Coffeella (Lepidoptera: Lyonetiidae) Population Dynamics in Chiapas, Mexico.”
#       Biological Control 51 (1): 51–60. doi:10.1016/j.biocontrol.2009.03.021.
#    Lomeli-Flores, J. Refugio, Juan F. Barrera, and Julio S. Bernal. 2010. “Impacts of Weather, Shade Cover and
#       Elevation on Coffee Leafminer Leucoptera Coffeella (Lepidoptera: Lyonetiidae) Population Dynamics and
#       Natural Enemies.” Crop Protection 29 (9): 1039–48. doi:10.1016/j.cropro.2010.03.007.
pobs = ObsPobs.de_csv(
    archivo='Suconusco_Chiapas.csv', col_tiempo='Día',
    corresp={
        'Juvenil': L_coffeella['juvenil'],
        'Para_larva': Parasitoide_larvas['juvenil']
    },
    factor=900 * 1000

)
# Factor: datos en Suconusco_Chiapas está por larvas/plantas; se asume que hay 1 panta cada 10 m2 (2mx5m).
# El factor de 100 cambia los datos de individuos/plantas a individuos/hectarias.


datos_elencanto = clima_csv(
    'Finca_El_Encanto.csv', چوڑائی=14.98916667, طول=-91.16527778, بلندی=480,
    تبدل_ستون={
        'Mes': 'تاریخ',
        'Lluvia': 'بارش',
        'Temp máx': 'درجہ_حرارت_زیادہ',
        'Temp mín': 'درجہ_حرارت_کم'
    }
)
ClimaElEncanto = Clima(datos_elencanto)

calibs = EspecCalibsCorrida(aprioris=True)

sim = Simulador([Red_café, ClimaElEncanto])
res = sim.simular(exper=El_Encanto, calibs=calibs, n_rep_estoc=10, n_rep_parám=10)
print('Valid antes de calibrador')
pprint(res.validar())
res.graficar('antes calibrador')

sensib = sim.sensib(exper=El_Encanto, n=10)
sensib.graficar('sensib antes calibrador')

sim.calibrar('El Encanto', exper=El_Encanto)

res_después = sim.simular(exper=El_Encanto, n_rep_estoc=10, n_rep_parám=10)
pprint(res_después.validar())
res_después.graficar('después calibrador')

sensib = sim.sensib(exper=El_Encanto, n=10)
sensib.graficar('sensib después calibrador')
