from REDES.INSECTOS import Simple
from REDES.REDES import Red

# Unos ejemplos del uso del módulo de insectos y del módulo de redes agroecológicas

print('Creando insectos...')
# Crear nuestros insectos
mosca = Simple('mosca')
araña = Simple('araña')

# Decidir quién come quién
araña.secome(mosca)
mosca.secome('cebolla')

# Guardar todo. Si quiere utilizar los mismos insectos en otra red, ya no será necesario crearlos como arriba.
mosca.guardar()
araña.guardar()

# Crear y probar la red agroecológica
red_cebolla = Red(nombre='red_cebolla', insectos=['mosca', 'araña'], cultivos=['cebolla'])
print('***', red_cebolla.insectos['mosca'].fases['Adulto'].dic['Depredadores'])
red_cebolla.ejec(poblaciones_iniciales={'mosca': {'Adulto': 100}, 'araña': {'Adulto': 0}})

red_cebolla.simul(paso=1, estado_cultivo=100000, tiempo_final=300, rep=100)

# Guardar los datos de los insectos
print('Guardando datos de insectos...')
red_cebolla.guardar()

# Calibrar la red según datos 'reales':
red_cebolla.datos = {'mosca': {'Adulto': (list(range(11)),
                                          [100, 25, 30, 33, 40, 50, 44, 12, 11, 9])
                               },
                     'araña': {'Adulto': (list(range(11)),
                                          [10, 4, 5, 3, 4, 5, 3, 1, 1, 3])
                               }
                     }

red_cebolla.calibrar(iteraciones=10, quema=0)
