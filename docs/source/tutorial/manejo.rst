Manejo
======
En Tiko'n, *manejo* se refiere a acciones que toman humanos para modificar el sistema agrícola.

Reglas
------
Una **regla** () tiene dos componentes: una **condición** () y una o más **acciones** (). Cuando se cumple la
condición, entonces se ejecutará la acción.

Condiciones
-----------
Las condiciones pueden ser según el tiempo o según el valor de un variable particular.

Temporales
^^^^^^^^^^

Variables
^^^^^^^^^


.. note::
   Las condiciones basades en valores de variables se evaluan **separadamente** para cada repetición estocástica
   y paramétrica del modelo.

Combinadas
^^^^^^^^^^
Igualmente puedes combinar varias condiciones con :class:`tikon.manejo.conds.CondY` y :class:`tikon.manejo.conds.CondO`.

Acciones
--------


Uso en modelos
--------------
