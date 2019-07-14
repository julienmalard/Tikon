A prioris
=========
Distribuciones *a priori* especifican rangos probables para los parámetros de un modelo. Se pueden especificar
por el usuario y después se tomarán en consideración para corridas de simulaciones y calibraciones.

Existen dos maneras de especificar una distribución a priori: por densidad y por forma analítica.

.. warning::

   Distribuciones *a priori* solamente se toman en cuenta automáticamente para corridas de calibraciones.
   Ver :ref:`espec-calibs` para más detalles.

Densidad
--------
Se puede especificar *a prioris* por un rango de dos valores y el nivel de confianza que el valor verdadero
se encuentre efectivamente en el rango. Tiko'n generará automáticamente una distribución que corresponde a
la especificación, y eso, tomando también en cuenta los límites teoréticos del parámetro.

Analíticas
----------
También se puede especificar un *a priori* directamente por su forma analítica.

Uso en modelos
--------------


Interacciones
^^^^^^^^^^^^^
En el caso de parámetros con interacciones, los a prioris especificados se aplicarán a la raíz del árbol de
interacciones del parámetro. Igualmente puedes especificar un nivel de interacción al cual aplicar el *a priori*.


.. note::

   Ver :doc:`/tutorial/ecs` para una explicación de niveles en árboles de ecuaciones, y :ref:`heredar-interacciones`
   para una descripción de cómo desactivar la propagación de *a prioris* a través los niveles de interacción.
