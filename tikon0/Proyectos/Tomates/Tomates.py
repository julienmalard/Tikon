from tikon0.Cultivo.NuevoCultivo import Cultivo
from tikon0.Manejo.Aplicación import Insecticida
from tikon0.Paisaje.NuevaParcela import Parcela
from tikon0.RAE.RedAE import Red

tomates = Cultivo('Tomate_var1', fuente='')

pesticida = Insecticida('muy tóxico', fuente='')

red_tomates = Red('Red tomates', fuente='')

parc = Parcela('Mi_parcela', cultivo=tomates, red=red_tomates)
parc.estab_lugar('')
parc.sembrar(tomates, 'Fecha')
parc.irrigar('Fechas', 'Cantidades')
parc.cosechar(tomates, 'Maturidad')
parc.aplicar(pesticida, 'Fecha')

parc.simular()
