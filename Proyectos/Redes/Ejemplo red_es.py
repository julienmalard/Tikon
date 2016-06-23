from RAE.INSECTOS import Sencillo
from RAE.REDES import Red

# Lo arriba simplement carga los módulos necesario de Tikon. Ignóralo.


# Hagamos una red sencilla!

# Primero, vamos a crear a nuestros insectos. Hagámoslos insectos con ciclos de vida sencillos para no tener que
# preocuparse por larvas, pupas, etc.
mosca = Sencillo('mosca')
araña = Sencillo('araña')

# Decidir quién se come a quíen
araña.secome(mosca)
mosca.secome('cebolla')

# Guardar todo. Es muy útil si quieres regresar y usar los mismos insectos después.
mosca.guardar()
araña.guardar()

# Crear la red agroecológica con los insectos que acabamos de crear
red_cebolla = Red(nombre='red_cebolla', insectos=['mosca', 'araña'], cultivos=['cebolla'])

# Dar poblaciones iniciales. Pondremos 100 moscas y 1 araña.
red_cebolla.ejec(poblaciones_iniciales={'mosca': {'Adulto': 100}, 'araña': {'Adulto': 1}})

# Correr la simulación
red_cebolla.simul(estado_cultivo={'cebolla': 100000}, tiempo_final=300)

# Guardar todo.
red_cebolla.guardar()

"""
Ahora, diviértete con tus propias redes!
Hay cinco etapas importantes (disculpe, que todavía es tecnología en beta):
1. Crear tus insectos y decidir quién se come a quién.
2. Guardar todos tus insectos.
3. Crear tu red agroecológica.
4. Establecer poblaciones iniciales y correr la simulación.
5. Guardar tu red agroecológica.
"""


# 1. Aquí es un ejemplo de cómo puedes crear un nuevo insecto (una avispa) que se come a las moscas y a las arañas:
avispa = Sencillo('avispa')
avispa.secome(araña)
avispa.secome(mosca)

# 2. Guardar lo que acabas de hacer.
mosca.guardar()
araña.guardar()
avispa.guardar()

# 3. Crear tu propia red.
mi_red_cebolla = Red(nombre='mi_red_cebolla', insectos=['avispa', 'araña', 'mosca'], cultivos=['cebolla'])

# 4. Poner las poblaciones iniciales y simular
mi_red_cebolla.ejec(poblaciones_iniciales={'mosca': {'Adulto': 100}, 'araña': {'Adulto': 1}, 'avispa': {'Adulto': 10}})
mi_red_cebolla.simul(estado_cultivo={'cebolla': 100000}, tiempo_final=300)

# 5. Guardar todo (siempre es buena idea)
mi_red_cebolla.guardar()
