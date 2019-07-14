.. image:: _estático/logos/Logo_Tikon.png
   :width: 250px
   :alt: Logo de Tiko'n
   :align: center

¡Bienvenidoas a la documentación de Tiko'n!
===========================================

.. image:: https://travis-ci.org/julienmalard/Tikon.svg?branch=master
   :target: https://travis-ci.org/julienmalard/Tikon
.. image:: (https://coveralls.io/repos/github/julienmalard/Tikon/badge.svg?branch=master
   :target: https://coveralls.io/github/julienmalard/Tikon?branch=master
.. image:: https://readthedocs.org/projects/tikon/badge/?version=latest
   :target: (https://tikon.readthedocs.io/es/latest/?badge=latest

.. image:: https://www.codefactor.io/repository/github/julienmalard/tikon/badge
   :target: (https://www.codefactor.io/repository/github/julienmalard/tikon
.. image:: https://api.codeclimate.com/v1/badges/855ebb601a34ec094956/maintainability
   :target: https://codeclimate.com/github/julienmalard/Tikon/maintainability

¿Qué es Tiko'n?
---------------
Tiko'n es un programa para desarrollar modelos de redes tróficas agroecológicas de manera sencilla, reproducible y
divertida.

¿Qué es un modelo de redes tróficas?
------------------------------------
Un modelo de redes tróficas es un modelo que representa las interacciones entre organismos vivos en un campo agrícola
(en general insectos y otros artrópodos). Predice el nivel de control biológico natural, las presiones futuras de plagas
dado factores como el clima y la presencia de insectos benéficos, y hacia permite predecir cuáles serían los
impacto de varias estrategias de manejo de plagas.

¿Por qué utilizar Tiko'n?
-------------------------
Redes tróficas con cosas muy difíciles a modelizar. Aun las más sencillas (3 insectos) presentan problemas como

#. Multitud de parámetros (15+ por insecto)
#. Inestabilidad matemática (dificultando predicciones fiables)
#. Multitud de posibilidades de ecuaciones en la literatura para cada fase de vida (reproducción, edad, transiciones, muertes, depredación)
#. Muy alta incertidumbre en los valores verdaderos de los parámetros
#. Pocos datos para calibración y validación
#. Requerimiento de conocimientos informáticos avanzados para conectar con modelos de cultivos externos o con predicciones de cambios climáticos

Así que si quieres hacer modelos tróficos pero te desaniman estos retos, ¡Tiko'n es para ti! Tiko'n manejará
todos los puntos arriba para ti, siempre dándote el nivel de control que quieres sobre los detalles de tu modelo,
nada menos, nada más.

#. Colección interna de la mayoría de ecuaciones para redes tróficas disponibles en la literatura, con selección automática de ecuaciones para principiantes
#. Posibilidad de agregar tus propias ecuaciones si quieres
#. Conexión automática con bases de datos y con predicciones y observaciones climáticas
#. Manejo automático de parametros y de cálculos de poblaciones y de depredación
#. Funcionalidades integradas para calibración y validación de modelos
#. Formato estandardizado para guardar y compartir modelos calibrados
#. Y, por supuesto, gráficos bonitos

Contenido
=========

.. toctree::
   :maxdepth: 2
   :caption: General

   general/intro
   general/instal
   general/estruc
   general/pubs
   general/agrad

.. toctree::
   :maxdepth: 2
   :caption: Tutorial

   tutorial/constr
   tutorial/insectos
   tutorial/cultivos
   tutorial/manejo
   tutorial/aprioris
   tutorial/ecs
   tutorial/clima
   tutorial/calibs_simul

.. toctree::
   :maxdepth: 2
   :caption: Desarrollo

   des/red
   des/módulos
   des/cultivos
   des/trad

.. toctree::
   :maxdepth: 2
   :caption: Referencia

   ref/red
   ref/insecto
   ref/clima
   ref/cultivo
   ref/manejo
   ref/general
   ref/resultados
