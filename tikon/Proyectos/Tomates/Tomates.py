from tikon.Cultivo.NuevoCultivo import Cultivo
from tikon.RAE.RedAE import Red
from tikon.Manejo.Aplicación import Insecticida
from tikon.NuevaParcela import Parcela

tomates = Cultivo('Tomate_var1', fuente='')

tomates.sembrar('Fecha')
tomates.irrigar('Fechas', 'Cantidades')
tomates.cosechar('Maturidad')

pesticida = Insecticida('tóxico', fuente='')
tomates.aplicar(pesticida, 'Fecha')

red_tomates = Red('Red tomates', fuente='')

parc = Parcela('Mi_parcela', cultivo=tomates, red=red_tomates)
parc.estab_lugar('')

parc.simular()
