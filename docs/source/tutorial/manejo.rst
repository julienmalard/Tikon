Manejo
======
En Tiko'n, *manejo* se refiere a acciones que toman humanos para modificar el sistema agrícola.

Aquí vamos a predecir el impacto de biocontrol con el modelo de *Opisina arenosella* que ya desarrollamos.

Cómo funciona
-------------
Una **regla** (:class:`~tikon.manejo.manejo.Regla`) tiene dos componentes: una **condición**
(:class:`~tikon.manejo.conds.Condición`) y una o más **acciones** (:class:`~tikon.manejo.acciones.Acción`).
Cuando se cumple la condición, Tiko'n ejecutará el acción. ¡Sencillo!

Las condiciones pueden ser según el tiempo (:class:`~tikon.manejo.conds.CondTiempo` y
:class:`~tikon.manejo.conds.CondCada`) o según el valor de un variable particular
(:class:`~tikon.manejo.conds.CondVariable`). Igualmente puedes combinar varias condiciones con
:class:`~tikon.manejo.conds.CondY` y :class:`~tikon.manejo.conds.CondO`.

.. note::
   Las condiciones basades en valores de variables se evaluan **separadamente** para cada repetición estocástica
   y paramétrica del modelo.

Biocontrol
----------

.. code-block:: python
