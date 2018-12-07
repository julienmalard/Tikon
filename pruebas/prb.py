from tikon.simulador import Simulador
from tikon.RAE.red_ae.red import RedAE
from tikon.RAE.orgs.insectos.gnrc import Sencillo

ins = Sencillo('sencillo')
red = RedAE(ins)

simul = Simulador(red)

res = simul.simular(10)

print(res)
