Estructura general
==================
La modelización agroecológica es un tema un poco más complicado que otros tipos de modelos por causa de su
complejidad y comportamiento dinámico. La estructura de Tiko'n toma en cuenta estos desafíos por su inclusión de
repeticiones estocásticas, incertidumbre paramétrica, y filosofía modular y flexible.

Aquí sigue una breve introducción a los términos específicos a Tiko'n.

Simulador
---------
Un :class:`~tikon.central.simulador.Simulador` es la unidad fundamental de un modelo en Tiko'n. Contiene
varios módulos (:class:`~tikon.central.módulo.Módulo`) que interactuan entre sí mismos.
Todas simulaciones y calibraciones se efectuan a través de un :class:`~tikon.central.simulador.Simulador`.

Módulos
-------
Cada :class:`~tikon.central.módulo.Módulo` en Tiko'n representa una parte del agroecosistema. Por ejemplo, existen
módulos para la red agroecológica, para el clima, para el cultivo y para el manejo humano.
Los módulos pueden intercambiar valores de variables en el transcurso de una simulación.

Experimentos
------------
Un :class:`~tikon.exper.exper.Exper` representa un experimento, o sea, una combinación de decisiones de observaciones
(reales o hipotéticas) para una simulación. Aun simulaciones sin datos observados implementan un experimento vacío
automáticamente.

Simulaciones
------------
Se efectuan simulaciones por llamar :func:`~tikon.central.simulador.Simulador.simular` con especificaciones
de escala temporal, repeticiones paramétricas y estocásticas, y experimento.
Adentro de cada simulación, el modelo se va a :func:`~tikon.central.simulador.Simulador.iniciar`,
:func:`~tikon.central.simulador.Simulador.correr`, y finalmente :func:`~tikon.central.simulador.Simulador.cerrar`.

Resultados
----------
Los resultados de simulación tienen su propia clase (:class:`~tikon.datos.res.ResultadosSimul`), la cual incluye
los resultados (:class:`~tikon.datos.res.ResultadosMódulo`) de cada módulo del simulador, los cuales en torno
contienen los resultados (:class:`~tikon.datos.res.Resultado`) de cada variable del módulo.
Resultados se pueden :func:`~tikon.datos.res.ResultadosSimul.validar` y también
:func:`~tikon.datos.res.ResultadosSimul.graficar`.

Parámetros
----------
Por supuesto, todo modelo necesita parámetros. En Tiko'n, los parámetros se implementan por
:class:`~tikon.ecs.árb_mód.Parám`, y cada parámetro puede tener varias calibraciones conteniendo distintas
distribuciones de valores (:class:`~tikon.ecs.dists.Dist`).


Ecuaciones
----------
El módulo :class:`~tikon.rae.red_ae.RedAE` implementa ecuaciones (:class:`~tikon.ecs.árb_mód.Ecuación`) para
representar cada fase del ciclo de vida de los insectos en la red. Las ecuaciones se pueden por supuesto modificar,
agregar, o desactivar según sus necesidades.
