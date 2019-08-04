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
Primero cargamos el modelo y sus calibraciones.

.. code-block:: python

   from tikon.ejemplos.calibs import obt_calib
   from tikon.ejemplos.proyectos.opisina_arenosella import modelo as mod
   from tikon.estruc.simulador import Simulador

   dir_calibs = 'Opisina arenosella, Perera et al. 1988'

   mod.red.cargar_calib(obt_calib(dir_calibs))
   mod.exper_A.cargar_calib(obt_calib(dir_calibs))

Ahora vamos a soltar parasitoides de *O. arenosella* cada 30 días.

.. code-block:: python

   from tikon.manejo.acciones import AgregarPob
   from tikon.manejo.conds import CondCada
   from tikon.manejo.manejo import Manejo, Regla

   acción = AgregarPob(mod.Paras_pupa['adulto'], 200000)
   cond = CondCada(30)
   manejo_dinámico = Manejo(Regla(cond, acción))

   simul = Simulador([mod.red, manejo_dinámico])
   res_tiempo = simul.simular(400, exper=mod.exper_A, n_rep_estoc=5)

   res_dinámicos.graficar('mis resultados aquí/temporales')


También podemos hacer control biológico más inteligente, y solamente soltar parasitoides cuando la población
de *O. arenosella* sube demasiado. En este ejemplo soltamos 200000 parasitoides adultos por hectárea cada vez que
tenemos una población de pupas de *O. arenosella* superior a 200000. Igualmente esperamos 30 días después de una
aplicación de parasitoides antes de poder considerar una nueva aplicación.

.. code-block:: python

   from tikon.manejo.conds import CondPoblación, SuperiorOIgual

   acción = AgregarPob(mod.Paras_pupa['adulto'], 200000)
   cond = CondPoblación(mod.Oarenosella['pupa'], SuperiorOIgual(200000), espera=30)
   manejo_dinámico = Manejo(Regla(cond, acción))

   simul = Simulador([mod.red, manejo_dinámico])
   res_dinámicos = simul.simular(400, exper=mod.exper_A, n_rep_estoc=5)

   res_dinámicos.graficar('mis resultados aquí/dinámicos')
