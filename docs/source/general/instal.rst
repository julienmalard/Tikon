Instalación
===========

Es muy fácil instalar Tiko'n. Primero necesitarás la versión más recién de `Python
<(https://www.python.org/downloads)>`_. Después, puedes instalar Tiko'n en la terminal con:

   :command:`pip install tikon`

Si quieres la versión más recién (en desarrollo), puedes obtenerla de GitHub directamente con:

   :command:`pip install git+git://github.com/julienmalard/tikon.git@master`

.. note::

   Si tienes Windows, es posible que tengas que instalar el ``C++ redistributable`` de
   `aquí <https://support.microsoft.com/es-gt/help/2977003/the-latest-supported-visual-c-downloads>`_.
   Toma la versión terminando en ``…x86.exe`` si tienes Python de 32 bits y en ``…x64.exe`` si tienes **Python**
   (no Windows) de 64 bits. Después, instálalo. Por razones obscuras, ``SciPy``, un paquete requerido por Tiko'n,
   no funciona en Windows sin éste.
