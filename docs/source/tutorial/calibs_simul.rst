Calibraciones y simulaciones
============================

Comportamiento automático
-------------------------
Si no se especifican calibraciones para una corrida, Tiko'n tomará una decisión razonable para ti.

* Si es una corrida de **simulación**, se tomará cada simulación disponible

Calibraciones específicas
-------------------------
Si quieres cambiar el comportamiento automático, puedes

Opciones avanzadas
------------------

A prioris
^^^^^^^^^

Correspondencia
^^^^^^^^^^^^^^^
Cuando se calibra un modelo con varios parámetros, no solamente importan los valores estimados de los parámetros
sino también las interacciones entre los parámetros si mismos. Es decir, en la calibración no se busca el valor
óptimo de cada parámetro individualmente sino un conjunto de valores para todos los parámetros
que da buenos resultados. Por eso es importante, tanto como sea posible, guardar las correlaciones entre los valores
de los parámetros calibrados y Tiko'n hará su posible para únicamente tomar valores de calibraciones que están
disponibles para todos los parámetros necesarios a la simulación.

Si quieres desactivar esta funcionalidad, se

Heredar interacciones
^^^^^^^^^^^^^^^^^^^^^
Parámetros en Tiko'n pueden tener interacciones con otros objetos, por ejemplo, en el caso de un parámetro de
eficacidad de depredación que también se ve influido por la identidad de la presa.
