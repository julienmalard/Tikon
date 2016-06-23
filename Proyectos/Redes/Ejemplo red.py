from RAE.INSECTOS import Sencillo
from RAE.REDES import Red

# Unos ejemplos del uso del módulo de insectos y del módulo de redes agroecológicas

# Crear nuestros insectos
mosca = Sencillo('mosca')
araña = Sencillo('araña')

# Decidir quién come quién
araña.secome(mosca)
mosca.secome('cebolla')

# Guardar todo. Si quiere utilizar los mismos insectos en otra red, ya no será necesario crearlos como arriba.
mosca.guardar()
araña.guardar()

# Crear y probar la red agroecológica
red_cebolla = Red(nombre='red_cebolla', insectos=['mosca', 'araña'], cultivos=['cebolla'])
red_cebolla.ejec(poblaciones_iniciales={'mosca': {'Adulto': 100}, 'araña': {'Adulto': 0}})

red_cebolla.simul(paso=1, estado_cultivo={'cebolla': 100000}, tiempo_final=300, rep=100)

# Guardar los datos de los insectos
red_cebolla.guardar()

# Calibrar la red según datos 'reales':
red_cebolla.datos = {'fictitios': {'mosca': {'Adulto': (list(range(10)),
                                                        [100, 25, 30, 33, 40, 50, 44, 12, 11, 9])
                                             },
                                   'araña': {'Adulto': (list(range(10)),
                                                        [10, 4, 5, 3, 4, 5, 3, 1, 1, 3])
                                             }
                                   }
                     }

# red_cebolla.calibrar(estado_cultivo={'cebolla': 100000}, iteraciones=10000, quema=100)
