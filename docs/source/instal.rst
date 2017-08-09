Instalación
===========

.. contents:: Contenido
   :depth: 3

Si sabes lo que estás haciendo
------------------------------
¡Felicitaciones! Tiko'n necesita Python 3.5+, NumPy, SciPy, y Matplotlib. Tiko'n sí mismo es un paquete de Python que se
puede conseguir con

   :command:`pip install tikon`

Si no sabes lo que estás haciendo (para Windows)
------------------------------------------------
Esto es para Windows. Es un poco complicado, así que si tienes dificultades no dudes en pedirme ayuda
(|correo|) para que te ahorres los dolores de cabeza que yo ya pasé.

Si estás usando Linux, no tengo ni idea cómo funciona pero me han dicho que es bastante más fácil que para los pobres
que todavía seguimos con Windows.

Si tienes un Mac, no tengo ni idea cómo funciona y parece que es bastante más difícil que para Windows.

Instalación de Python
^^^^^^^^^^^^^^^^^^^^^
Primer que todo, hay que instalar Python. Puedes descargar la versión la más recién de aquí (https://www.python.org/downloads).
Mejor descarges la versión 3.6 de 32 bits, porque así Tiko'n te podrá ayudar un poco con la instalación de los paquetes
adicionales necesarios.

Instalación de Tiko'n
^^^^^^^^^^^^^^^^^^^^^
Si instalaste Python 3.6 de 32 bits tal como te dije, no deberías tener problema cualquier [#f1]_.

1. Primero, tienes que ir `aquí <https://www.microsoft.com/es-ES/download/details.aspx?id=53840>`_ y
   descargar el ``C++ 2015 redistributable`` (toma la versión terminando el ``…x86.exe`` si tienes Python de 32 bits
   (si no lo sabes, toma éste) y en ``…x64.exe`` si tienes *Python* (no Windows) de 64 bits. Después, instálalo. Por
   razones obscuras, `SciPy`, una extensión utilizada por Tiko'n, no funciona en Windows sin éste.
2. Ahora, puedes instalar Tiko'n con la comanda siguiente en la línea de comanda:

      :command:`pip install tikon`

Tiko'n debería instalarse y todos los otros paquetes que necesitar automáticamente [#f2]_. Si aún así te da problemas,
no dudes en escribirme (|correo|).

Uso con PyCharm
^^^^^^^^^^^^^^^
Para personas que piensan hacer más con Tiko'n que usar el IGU (eventual), recomiendo muy fuertemente que usen la versión
Comunitaria (gratis) de `PyCharm <https://www.jetbrains.com/pycharm)>`_. PyCharm es para Python lo que Word y OpenOffice
son para documentos de texto, y te salvará de muchos dolores de cabeza (por una cosa, te dice dónde has hecho un error,
y no se congela cada 30 segundos, al contrario del editor automático que viene con Python).

Es bastante fácil usar PyCharm; después de instalarlo, simplemente hay que abrir un nuevo proyecto en el editor y
empezar a escribir tu código. Si quieres contribuir a Tiko'n, puedes usar PyCharm para conectar tu versión con la página
de Tiko'n en GitHub (así siempre tendrás la versión más recién). Contáctame (|correo|) si estás interesada.

.. rubric:: Notas

.. [#f1] El problema con Python es que, mientras que es mucho más fácil para leer o escribir que otras lenguas (si no me crees,
       busca Fortran o C++), también es bastante más lento. Por eso, códigos Python que involucran muchos cálculos numéricos
       se escriben con extensiones en Fortran o en C para aumentar la velocidad un poco. No te preocupes, ¡que Tiko'n no tiene
       nada en Fortran o C! Es puro Python. Pero desafortunadamente para sus funciones matemáticas necesita unos paquetes adicionales
       de Python (NumPy, SciPy y Matplotlib), y ellos sí tienen extensiones raras.

       Bueno, si todo esto te parece un poco incómodo, estoy de acuerdo. Hay una nueva lengua de programación llamada
       `Julia <http://julialang.org/>`_ que es tan rápida como C y tan intuitiva como Python, y por lo tanto no tiene nada de
       extensiones ajenas en Fortran o en C. Pero me di cuenta demasiado tarde y ahora no voy a reescribir todo el programa de
       Tiko'n en Julia (después de todo, tengo una tesis que escribir). Lo siento.
.. [#f2] Si no instalaste Python 3.6 de 32 bits como te dije, pero como la mayoría de la gente normal no sabes como compilar
       C++ y Fortran en tu propia computadora, es tu problema. No, es broma. Pero de verdad vas a sufrir un poco. Primero,
       recomiendo que vayas a `este sitio <http://www.lfd.uci.edu/~gohlke/pythonlibs>`_, donde un profesor muy amable ya
       compiló las extensiones para ti. Puedes descargar los archivos precompilados para tu versión de Python
       (por ejemplo, `scipy-0.18.1-cp36-cp36m-win32.whl` para SciPy en Python 3.6 de 32 bits) y después instalarlos
       directamente de tu directorio local con pip así como en el ejemplo:
       `pip install C:\\Users\\jeanne\\Downloads\\numpy‑1.11.3+mkl‑cp36‑cp36m‑win32.whl`.
       Tienes que instalarlos en el orden siguiente: `NumPy`, `SciPy`, `Matplotlib`, y por fin `PyMC`, sino tendrás
       muchos muchos problemas. *Después* de eso, puedes instalar Tiko'n con `pip install tikon`.