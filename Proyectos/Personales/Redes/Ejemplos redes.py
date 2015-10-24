from REDES.INSECTOS import Simple
from REDES.REDES import Red

# Unos ejemplos del uso del módulo de insectos y del módulo de redes agroecológicas

# Crear nuestros insectos
mosca = Simple('mosca')
araña = Simple('araña')

# Decidir quién come quién
araña.secome(mosca)
mosca.secome('cebolla')

# Crear la red agroecológica
red_cebolla = Red('red_cebolla', [mosca, araña])

red_cebolla.ejec(poblaciones_iniciales={'mosca': {'Adulto': 100}, 'araña': {'Adulto': 10}})

red_cebolla.simul(paso=1, estado_cultivo=100000, tiempo_final=100)

