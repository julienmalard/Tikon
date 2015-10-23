from REDES.INSECTOS import *
from REDES.REDES import *

# Unos ejemplos del uso del módulo de insectos y del módulo de redes agroecológicas
person = input('Enter your name: ')
print('Hello', person)

# Crear nuestros insectos
mosca = Simple('mosca')
araña = Simple('araña', huevo=True)

# Decidir quién come quién
araña.secome(mosca)
mosca.secome('cebolla')

# Crear la red agroecológica
red_cebolla = Red('red_cebolla', [mosca, araña])

red_cebolla.ejec(poblaciones_iniciales={'mosca': 100, 'araña': {'Adulto': 10, 'Huevo': 50}})

red_cebolla.simul(1, estado_cultivo=100000, tiempo_final=100)

