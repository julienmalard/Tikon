import os
from subprocess import run

directorio = os.path.split(os.path.realpath(__file__))[0]

directorio_móds = os.path.join(directorio, 'Módulos')

lista_móds = ['numpy-1.11.0+mkl-cp35-cp35m-win32.whl',
              'matplotlib-1.5.1-cp35-none-win32.whl',
              'scipy-0.17.1-cp35-cp35m-win32.whl',
              'pymc-2.3.6-cp35-none-win32.whl']

for mód in lista_móds:
    comanda = 'pip install %s' % os.path.join(directorio_móds, mód)

    run(comanda)
