.. _espec-calibs:

Calibraciones y simulaciones
============================
En Tiko'n, una *calibración* se refiere a un conjunto de valores para los parámetros de un modelo, todos calibrados
en conjunto. Una *simulación* se refiere a cualquier ejecución del modelo. Por ejemplo, calibrar un modelo generalmente
requiere la ejecución de una cantidad importante de simulaciones.

Por lo tanto, cada *simulación* normal se corre con una especificación de cuales `calibraciones` tomar en cuenta
para establecer los valores de sus parámetros.

Comportamiento automático
-------------------------
Si no se especifican calibraciones para una corrida, Tiko'n tomará una decisión razonable para ti.

* Si es una corrida de **simulación**, se tomará cada calibración disponible, y se ignorarán *a prioris* especificados
* Si es una corrida de **calibración**, se tomarán primero los *a prioris* especificados, y, para los parámetros sin aprioris, se generarán distribuciones a base de las calibraciones ya existentes.

Calibraciones específicas
-------------------------
Si quieres cambiar el comportamiento automático, puedes especificar cuáles calibraciones existantes quieres incluir
en la corrida.

Opciones avanzadas
------------------
Puedes cambiar el comportamiento automático por pasar un objeto :class:`~tikon.estruc.simulador.EspecCalibsCorrida`
a la función de simulación :func:`~tikon.estruc.simulador.Simulador.simular` del
:class:`~tikon.estruc.simulador.Simulador` (e igualmente a las que la llaman
indirectamente, como :func:`~tikon.estruc.simulador.Simulador.calibrar` y
:func:`~tikon.estruc.simulador.Simulador.sensib`).
:class:`~tikon.estruc.simulador.EspecCalibsCorrida` toma opciones para especificar el uso de *a prioris*, de
correspondencia entre parámetros, y de herencia de interacciones.

A prioris
^^^^^^^^^
Puedes especificar si se deberían emplear distribuciones *a prioris* para los parámetros donde han sido especificados.
En este caso, se ignorarán todas otras calibraciones disponibles para los parámetros con *a prioris* disponibles.

Correspondencia
^^^^^^^^^^^^^^^
Cuando se calibra un modelo con varios parámetros, no solamente importan los valores estimados de los parámetros
sino también las interacciones entre los parámetros sí mismos. Es decir, en la calibración no se busca el valor
óptimo de cada parámetro individualmente sino un conjunto de valores para todos los parámetros
que da buenos resultados. Por eso es importante, tanto como sea posible, guardar las correlaciones entre los valores
de los parámetros calibrados y Tiko'n hará su posible para únicamente tomar valores de calibraciones que están
disponibles para todos los parámetros necesarios a la simulación.

Si quieres desactivar esta funcionalidad, puedes indicarlo así:


.. _heredar-interacciones:

Heredar interacciones
^^^^^^^^^^^^^^^^^^^^^
Parámetros en Tiko'n pueden tener interacciones con otros objetos, por ejemplo, en el caso de un parámetro de
eficacidad de depredación que también se ve influido por la identidad de la presa.
La opción automática es que cada parámetro, si le faltan calibraciones, puede heredar las calibraciones o *a prioris*
del nivel de interacción subyacente.

.. note::
   Ver :doc:`/tutorial/ecs` para una explicación de niveles en árboles de ecuaciones.
