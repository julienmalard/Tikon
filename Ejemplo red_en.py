from REDES.INSECTOS import Simple
from REDES.REDES import Red

# Stuff above this line just loads the other modules needed to make a food web. Ignore it.


# Let's make a simple food web!

# First, we're going to create our insects. Let's make them simple insects so we won't have to worry about larvae,
# pupae, etc.
fly = Simple('fly')
spider = Simple('spider')

# Decide who eats who
spider.secome(fly)
fly.secome('onion')

# Save everything. This is useful so that you can come back and use these insects later.
fly.guardar()
spider.guardar()

# Create the food web with the insects we just created
onion_food_web = Red(nombre='onion_food_web', insectos=['fly', 'spider'], cultivos=['onion'])

# Give starting populations. We will start with 100 flies and 1 spider
onion_food_web.ejec(poblaciones_iniciales={'fly': {'Adulto': 100}, 'spider': {'Adulto': 1}})

# Run the simulation
onion_food_web.simul(estado_cultivo={'onion': 100000}, tiempo_final=300)

# Save the data
onion_food_web.guardar()

"""
Have fun making your own food webs now!
There are 5 important steps (sorry this is still beta technology):
1. Create your new insects and choose who eats whom
2. Save all your insects
3. Create your food web
4. Set starting populations and run your simulation
5. Save your food web
"""

"""
# 1. Here is hhow you can make a new insect (a wasp) that eats spiders and flies:
wasp = Simple('wasp')
wasp.secome(spider)
wasp.secome(fly)

# 2. Save what you've just created
fly.guardar()
spider.guardar()
wasp.guardar()

# 3. Make your food web
my_food_web = Red(nombre='my_food_web', insectos=['wasp', 'spider', 'fly'], cultivos=['onion'])

# 4. Set starting populations and simulate
my_food_web.ejec(poblaciones_iniciales={'fly': {'Adulto': 100}, 'spider': {'Adulto': 1}, 'wasp': {'Adulto': 10}})
my_food_web.simul(estado_cultivo={'onion': 100000}, tiempo_final=300)

# 5. Save everything (always a good idea)
my_food_web.guardar()

"""
