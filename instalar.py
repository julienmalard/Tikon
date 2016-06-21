import os
import sys
from subprocess import run

directorio = os.path.split(os.path.realpath(__file__))[0]

directorio_móds = os.path.join(directorio, 'Módulos')

directorio_python = os.path.split(sys.executable)[0]

lista_móds = ['numpy-1.11.0+mkl-cp35-cp35m-win32.whl',
              'matplotlib-1.5.1-cp35-none-win32.whl',
              'scipy-0.17.1-cp35-cp35m-win32.whl',
              'pymc-2.3.6-cp35-none-win32.whl']

for mód in lista_móds:
    comanda = '%s install %s' % (os.path.join(directorio_python, 'Scripts', 'pip'),
                                 os.path.join(directorio_móds, mód))

    run(comanda)

# Verificar que todo este bien:
try:
    import numpy as np
    import scipy as sp
    import pymc
except ImportError:
    raise ImportError('Error: No se instalaron todos los módulos necesarios.')

try:
    import scipy.stats as estad
    prueba = estad.norm()
except ImportError:
    raise ImportError('¡Error! Por experencia personal, probablemente es porque no instalaste la versión del'
                      '"Microsoft C++ 2015 redistributable" x86.')
