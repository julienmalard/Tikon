from tikon.simulador import Simulador
from tikon.rae.red_ae.red import RedAE
from tikon.rae.orgs.insectos.gnrc import Sencillo, MetamCompleta

oruga = MetamCompleta('oruga')
araña = Sencillo('araña')
araña.secome(oruga)

red = RedAE([oruga, araña])

simul = Simulador(red)

res = simul.simular(10, n_rep_parám=17, n_rep_estoc=30)

print(res)
