from tikon.central import Exper, Parcela, GeomParcela
from tikon.ejemplos.proyectos.lotka_volterra.modelo import modelo

exper = Exper('P1', Parcela('P1', geom=GeomParcela((7.297, 79.865))))
modelo.simular("base", exper)
