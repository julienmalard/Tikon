from tikon.simulador import Simulador
from tikon.RAE.red_ae.red import RedAE
from tikon.RAE.orgs.insectos.gnrc import Sencillo, MetamCompleta

oruga = MetamCompleta('oruga')
araña = Sencillo('araña')
araña.secome(oruga)

red = RedAE([oruga, araña])

simul = Simulador(red)

res = simul.simular(10)

print(res)
