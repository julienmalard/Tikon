Contribuir datos
================
Un modelo no es mejor que los datos que lo alimentan. Lo más compartimos nuestros datos, lo mejor se volverá el
programa para todas las usuarias.

Contribuir observaciones
------------------------
Puedes contribuir bases de datos de observaciones de campo.

.. code-block:: python
   from tikon.ejemplos.datos import guardar_datos

   guardar_datos(
       'aquí/están/mis datos.csv',
       nombre='Yo et al., 2019',
       módulo='red',
       variable='Pobs',
       unidades='individuos por ha',
       ref=None  # puedes incluir una referencia Bibtex
   )

Contribuir calibraciones
------------------------
Ver :ref:`guardar_y_cargar` para instrucciones sobre cómo guardar tus calibraciones en Tiko'n.

Cómo compartir
--------------
La manera la más fácil de compartir los datos es de clonar una versión local de Tiko'n. Después, puedes hacer un
`commit` y compartir tus datos y calibraciones en GitHub con el resto de la comunidad.
