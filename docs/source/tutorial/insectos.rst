Insectos
========
Tiko'n implementa una gran variedad de ciclos de vida de insectos a través de subclases especiales de
:class:`~tikon.rae.orgs.insectos.Insecto`.

.. note::
   Tiko'n toma una vista *ecológica* de lo que es un insecto. Es decir, si come como un insecto y se come como un
   insecto, entonces *es* un insecto por lo que le importa a Tiko'n.

   Así que no te sorprendes al ver arañas y gusanos en las listas de insecto. Sé que entomólogicamente es una herecía,
   pero programáticamente es la mejor solución.

Cada insecto viene con sus etapas (huevo, larva, etc.) y las ecuaciones correspondientes ya especificadas.

Sencillo
--------
El tipo de insecto más sencillo posible. Por lo tanto es también generalmente inútil, pruebas teoréticas a parte.
Solamente lleva una forma adulta, y se implementa con la clase :class:`~tikon.rae.orgs.insectos.Sencillo`.

Metamórfosis completa
---------------------
Tiko'n lleva la clase :class:`~tikon.rae.orgs.insectos.MetamCompleta` para representar a insectos con ciclos de vida
completos (de huevo a adulto, pasando por una pupa).

Metamórfosis incompleta
-----------------------
Insectos con ciclos de vida incompletos (sin pupa) se pueden representar con la clase
:class:`~tikon.rae.orgs.insectos.MetamIncompleta`.

Parasitoides
------------
Parasitoides, aunque técnicamente por su mayor parte insectos con metamórfosis completa, se representan por su
propia clase (:class:`~tikon.rae.orgs.insectos.Parasitoide`) porque se debe tomar en cuenta el hecho de que su
fase juvenil se desarrolla adentro de su huésped.

Esfécidos
---------
Esfécidos son avispas similares a parasitoides pero que paralizan e inactivan su presa al momento del parasitismo,
lo cual puede se interior o exterior. Se deben representar de manera distinta
(:class:`~tikon.rae.orgs.insectos.Esfécido`) a paridoides convencionales, porque
la presa se quita del ecosistema al momento del acto de parasitismo y no al momento de la emergencia de la avispa
adulta.

Cambiar ecuaciones
------------------
Puedes modificar las ecuaciones empleadas para un insecto en particular.

Cambiar etapas
--------------
Si quieres cambiar la estructura de las etapas de un insecto, también puedes implementar una clase para un nuevo tipo de
insecto (ver :ref:`nuevos-insectos`).
