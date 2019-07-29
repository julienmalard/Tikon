Insectos
========
Tiko'n implementa una gran variedad de ciclos de vida de insectos a través de subclases especiales de
:class:`~tikon.rae.orgs.insectos.ins.Insecto`.

.. note::
   Tiko'n toma una vista *ecológica* de lo que es un insecto. Es decir, si come como un insecto y se come como un
   insecto, entonces *es* un insecto por lo que le importa a Tiko'n.

   Así que no te sorprendes al ver arañas y gusanos en las listas de insecto. Sé que entomólogicamente es una herecía,
   pero programáticamente es la mejor solución.

Cada insecto viene con sus etapas (huevo, larva, etc.) y las ecuaciones correspondientes ya especificadas.

Sencillo
--------
El tipo de insecto más sencillo posible. Por lo tanto es también generalmente inútil, pruebas teoréticas a parte.
Solamente lleva una forma adulta, y se implementa con la clase :class:`~tikon.rae.orgs.insectos.ins.Sencillo`.

Metamórfosis completa
---------------------
Tiko'n lleva la clase :class:`~tikon.rae.orgs.insectos.gnrc.MetamCompleta` para representar a insectos con ciclos de vida
completos (de huevo a adulto, pasando por una pupa).

.. code-block::python
   from tikon.rae.orgs.insectos import MetamCompleta

   mosca = MetamCompleta('mosca')

Metamórfosis incompleta
-----------------------
Insectos con ciclos de vida incompletos (sin pupa) se pueden representar con la clase
:class:`~tikon.rae.orgs.insectos.gnrc.MetamIncompleta`.

.. code-block::python
   from tikon.rae.orgs.insectos import MetamIncompleta

   mosca = MetamIncompleta('mosca')

   # Se puede crear insectos que pasan directamente del huevo al adulto
   araña = MetamIncompleta('araña', njuvenil=0)

Todos insectos de tipos :class:`~tikon.rae.orgs.insectos.ins.Sencillo`,
:class:`~tikon.rae.orgs.insectos.ins.MetamCompleta` o :class:`~tikon.rae.orgs.insectos.ins.MetamIncompleta`
pueden ser depredadores:


.. code-block::python
   araña.secome(mosca)

Parasitoides
------------
Parasitoides, aunque técnicamente por su mayor parte insectos con metamórfosis completa, se representan por su
propia clase (:class:`~tikon.rae.orgs.insectos.paras.Parasitoide`) porque se debe tomar en cuenta el hecho de que su
fase juvenil se desarrolla adentro de su huésped.


.. code-block::python
   from tikon.rae.orgs.insectos import Parasitoide

   avispa = Parasitoide('avispa')

   avispa.parasita(mosca, etps_entra='juvenil', etp_emerg='pupa')

Esfécidos
---------
Esfécidos son avispas similares a parasitoides pero que paralizan e inactivan su presa al momento del parasitismo,
lo cual puede se interior o exterior. Se deben representar de manera distinta
(:class:`~tikon.rae.orgs.insectos.paras.Esfécido`) a paridoides convencionales, porque
la presa se quita del ecosistema al momento del acto de parasitismo y no al momento de la emergencia de la avispa
adulta.


.. code-block::python
   from tikon.rae.orgs.insectos import Esfécido

   esfécido = Esfécido('esfécido')

   esfécido.captura(araña, etps_presa='adulto')


Cambiar ecuaciones
------------------
Puedes modificar las ecuaciones empleadas para un insecto en particular.

.. code-block::python
   from tikon.rae.orgs.insectos import Esfécido

   araña.activar_ec(categ='Edad', subcateg='Ecuación', ec='Días grados')

   esfécido.captura(araña, etps_presa='adulto')
