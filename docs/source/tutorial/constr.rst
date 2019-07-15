Construir una red
=================
En este ejemplo vamos a construir nuestra propria red trófica.

Especificar insectos
--------------------
Primero especificaremos nuestros insectos presentes, una oruga y dos parasitoides (ver :doc:`insectos`
para la lista completa de clases disponibles).

.. code-block:: python

   from tikon.rae.orgs.insectos import MetamCompleta, Sencillo, Parasitoide
   from tikon.rae.red_ae import RedAE

   Oarenosella = MetamCompleta('O. arenosella', njuvenil=5)
   Paras_larvas = Parasitoide('Parasitoide larvas', pupa=True)
   Paras_pupa = Parasitoide('Parasitoide pupa')

   Paras_larvas.parasita(Oarenosella, ['juvenil_3', 'juvenil_4', 'juvenil_5'], etp_emerg='juvenil_5')
   Paras_pupa.parasita(Oarenosella, 'pupa', etp_emerg='pupa')

   red = RedAE([Oarenosella, Paras_larvas, Paras_pupa])


A prioris
---------
Aquí vamos a cargar las distribuciones a prioris para los parámetros de la red. Los tienes que especificar manualmente
para cada experimento.

.. warning::
   Es **muy importante** establecer buenos *a prioris* para calibraciones. Las limitaciones de algoritmos existentes
   de calibración de estos tipos de modelos hacen primordial la especificación de *a prioris* razonables y bastante
   precisos para todos los parámetros del modelo.

En este caso ya especificamos nuestros a prioris en un documento separado así que los vamos a cargar directamente.

.. code-block:: python

   from tikon.ejemplos.opisina_arenosella.a_prioris import a_prioris
   red.espec_aprioris(a_prioris)


El experimento
--------------
Aquí se conecta la red con observaciones de campo a través de un experimento (:class:`~tikon.exper.exper.Exper`).

.. code-block:: python

   from tikon.ejemplos.datos import obt_datos
   from tikon.exper.exper import Exper
   from tikon.rae.red_ae.obs import ObsPobs

   # Datos de observaciones
   datos = obt_datos('Perera et al 1988/Oarenosella_A.csv')

   # Se trata de observaciones de poblaciones (y no de otro variable, como depredación).
   pobs = ObsPobs.de_csv(
       datos,
       col_tiempo='Día',
       corresp={
           'Estado 1': Oarenosella['juvenil_1'],
           'Estado 2': Oarenosella['juvenil_2'],
           'Estado 3': Oarenosella['juvenil_3'],
           'Estado 4': Oarenosella['juvenil_4'],
           'Estado 5': Oarenosella['juvenil_5'],
           'Pupa': Oarenosella['pupa'],
           'Para_larva_abs': Paras_larvas['juvenil'],
           'Para_pupa_abs': Paras_pupa['juvenil']
       },
       factor=655757.1429 / 500  # para convertir a individuos por ha
   )

   exper_A = Exper('Sitio A', pobs)


Calibración
-----------
Ahora vamos a calibrar nuestro modelo. Primero creamos un :class:`~tikon.estruc.simulador.Simulador` para poder correr
simulaciones y calibraciones. En nuestro ejemplo sencillo el simulado solamente tiene un módulo (la red), pero
se podrían incluir clima, manejo, o cultivos también.

.. code-block:: python

   from tikon.estruc.simulador import Simulador

   simul = Simulador(red)

   simul.calibrar('Sitio A', exper=exper_A)

Vamos a guardar los resultados de la calibración. Tiko'n también automáticamente calibra las poblaciones iniciales
para etapas cuyas poblaciones no se observaron en el experimento, así que guardaremos la calibración del
experimento también.

.. code-block:: python

   simul.guardar_calib('calibs Sitio A')
   exper_A.guardar_calib('calibs Sitio A')


Validación
----------
En este ejemplo vamos a hacer trampa y validar con los mismos datos de calibración.
Primero hacemos una simulación normal, y despues vamos a :func:`tikon.result.res.ResultadosSimul.validar` los
resultados. También los podremos :func:`tikon.result.res.ResultadosSimul.graficar`.

Las observaciones especificadas arriba quedaron vinculadas en los resultados y por eso se tomarán en cuenta
en la validación y en los gráficos.

.. code-block:: python

   res = simul.simular(exper=exper_A)
   pprint(res.validar())

   res.graficar('gráficos Sitio A')

Guardar y cargar
----------------
