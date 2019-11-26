from tikon.central import Exper, Parcela, Modelo
from tikon.móds.rae.orgs.insectos import Sencillo
from tikon.móds.rae.red import RedAE
from tikon.móds.trampa.mód import Trampas
from tikon.móds.trampa.trampas import Trampa

trampa = Trampa('Amarilla')

móp_trampas = Trampas(trampa)

exper = Exper('exper', Parcela('parc'))

ins = Sencillo('sencillo')
red = RedAE(ins)
modelo = Modelo([móp_trampas, red])
