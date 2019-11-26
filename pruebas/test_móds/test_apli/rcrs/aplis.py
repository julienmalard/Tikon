from tikon.central import Exper, Parcela, Modelo
from tikon.móds.apli.apli import Aplicaciones
from tikon.móds.apli.prods import Producto
from tikon.móds.rae.orgs.insectos import Sencillo
from tikon.móds.rae.red import RedAE

producto = Producto('Peligroso')

aplicaciones = Aplicaciones(producto)

exper = Exper('exper', Parcela('parc'))

ins = Sencillo('sencillo')
red = RedAE(ins)
modelo = Modelo([aplicaciones, red])
