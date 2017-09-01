import os
import platform
import shutil
import sys
import urllib.request
from subprocess import run
from warnings import warn as avisar

from setuptools import setup, find_packages

"""
Usuarios de Windows pueden tener problemas particularmente frustrantes para instalar los paquetes SciPy, NumPy, y
PyMC que necesita Tiko'n. Por eso vamos a intentar ayudarlos un poco aquí. No funciona perfectamente y para todas
las versiones de Windows, pero es mejor que nada.
Lo mismo aplica para PyMC en Mac, pero no tengo ni idea cómo ayudarte allí.
"""

so = platform.system()
bits = platform.architecture()[0][:2]

directorio = os.path.split(os.path.realpath(__file__))[0]
directorio_python = os.path.split(sys.executable)[0]
directorio_móds = os.path.join(directorio, 'Módulos')

versión_python = str(sys.version_info.major) + str(sys.version_info.minor)

try:
    import numpy as np
except ImportError:
    np = None

try:
    import matplotlib
except ImportError:
    matplotlib = None

try:
    import scipy.stats as estad
except ImportError:
    estad = None

try:
    import pymc
except ImportError:
    pymc = None

info_paquetes = {'numpy': {'versión': '1.13.1',
                           'formato_archivo': 'numpy-{versión}+mkl-cp{v_py}-cp{v_py}m-{sis}.whl',
                           '35': {
                               'Windows': {
                                   '32': {'id_dropbox': None
                                          },
                                   '64': {'id_dropbox': None
                                          }
                               }
                           },
                           '36': {
                               'Windows': {
                                   '32': {'id_dropbox': 'y66rav81q0i9gtu/numpy-1.11.3%2Bmkl-cp36-cp36m-win32.whl'
                                          },
                                   '64': {'id_dropbox': None
                                          }
                               }
                           },
                           },
                 'scipy': {'versión': '0.19.1',
                           'formato_archivo': 'scipy-{versión}-cp{v_py}-none-{sis}.whl',
                           '35': {
                               'Windows': {
                                   '32': {'id_google': None
                                          },
                                   '64': {'id_google': None
                                          }
                               }
                           },
                           '36': {
                               'Windows': {
                                   '32': {'id_dropbox': '46vls88hkpohki8/scipy-0.19.1-cp36-cp36m-win32.whl'
                                          },
                                   '64': {'id_google': None
                                          }
                               }
                           },
                           },
                 'matplotlib': {'versión': '2.0.0',
                                'formato_archivo': 'matplotlib-{versión}-cp{v_py}-none-{sis}.whl',
                                '35': {
                                    'Windows': {
                                        '32': {'id_google': None
                                               },
                                        '64': {'id_google': None
                                               }
                                    }
                                },
                                '36': {
                                    'Windows': {
                                        '32': {'id_google': '0B8RjC9bwyAOwRDlIU2x1YlY0U1U'
                                               },
                                        '64': {'id_google': None
                                               }
                                    }
                                },
                                },
                 'pymc': {'versión': '2.3.6',
                          'formato_archivo': 'pymc-{versión}-cp{v_py}-none-{sis}.whl',
                          '35': {
                              'Windows': {
                                  '32': {'id_google': None
                                         },
                                  '64': {'id_google': None
                                         }
                              }
                          },
                          '36': {
                              'Windows': {
                                  '32': {'id_google': '0B8RjC9bwyAOwTXlFQjZVYWczUTA'
                                         },
                                  '64': {'id_google': None
                                         }
                              }
                          },
                          },
                 'statsmodels': {
                     'versión': '0.8.0',
                     'formato_archivo': 'statsmodels-{versión}-cp{v_py}-cp{v_py}m-{sis}.whl',
                     '35': {
                         'Windows': {
                             '32': {'id_dropbox': None
                                    },
                             '64': {'id_dropbox': None
                                    }
                         }
                     },
                     '36': {
                         'Windows': {
                             '32': {'id_dropbox': 'obcypgvwheghb78/statsmodels-0.8.0-cp36-cp36m-win32.whl'
                                    },
                             '64': {'id_dropbox': None
                                    }
                         }
                     },
                 }
                 }


def _actualizar_pip():
    print('Actualizando pip...')
    comanda_pip = '%s install --upgrade pip' % (os.path.join(directorio_python, 'Scripts', 'pip'))
    run(comanda_pip)


def _descargar_whl(nombre, v_py, sis, b):
    print('Descargando paquete "{}"...'.format(nombre))
    llave = url = None

    repositorios = {'id_google': 'https://drive.google.com/uc?export=download&id={}',
                    'id_dropbox': 'https://www.dropbox.com/s/{}?dl=1'}

    for r, u in repositorios.items():
        try:
            llave = info_paquetes[nombre][v_py][sis][b][r]  # type: str
        except KeyError:
            pass
        if llave is not None:
            url = u.format(llave)
            break

    if url is None:
        avisar('No existe descarga para paquete {} en {} bits.'.format(nombre, bits))
        return False

    nombre_archivo = info_paquetes[nombre]['formato_archivo']
    urllib.request.urlretrieve(url, os.path.join(directorio_móds, nombre_archivo))

    return True


def _instalar_whl(nombre):
    nombre_archivo = info_paquetes[nombre]['formato_archivo']

    if os.path.isfile(os.path.join(directorio_móds, nombre_archivo)):
        éxito = True
    else:
        éxito = _descargar_whl(nombre, v_py=versión_python, sis=so, b=bits)

    if éxito:
        print('Instalando paquete "{}"...'.format(nombre))

        comanda = '%s install %s' % (os.path.join(directorio_python, 'Scripts', 'pip'),
                                     os.path.join(directorio_móds, nombre_archivo))
        run(comanda)


def instalar_requísitos():
    print('Instalando paquetes requísitos...')

    lista_paquetes = []

    if np is None:
        lista_paquetes.append('numpy')

    if matplotlib is None:
        lista_paquetes.append('matplotlib')

    if estad is None:
        lista_paquetes.append('scipy')

    if pymc is None:
        lista_paquetes.append('pymc')

    if len(lista_paquetes):

        if not os.path.exists(directorio_móds):
            os.makedirs(directorio_móds)
            dir_creado = True
        else:
            dir_creado = False

        # Actualizar Pip
        _actualizar_pip()

        # Instalar cada paquete necesario
        for paq in lista_paquetes:
            _instalar_whl(paq)

        if dir_creado:
            shutil.rmtree('Módulos')

    # Verificar que todo esté bien:
    try:
        import numpy as _
        import scipy as _
        import pymc as _
        import matplotlib as _
    except ImportError:
        _ = None
        pass

    try:
        import scipy.stats as _
        _.norm()
        print('¡Todo bien! Los paquetes Python necesarios han sido instalados.')

    except ImportError:
        _ = None
        avisar('¡Error! Por experencia personal, probablemente es porque no instalaste la versión del'
               '"Microsoft C++ 2015 redistributable" {}.\n'
               'Lo puedes conseguir de "https://www.microsoft.com/es-ES/download/details.aspx?id=48145".'
               .format('x86' if bits == '32' else 'x64')
               )


if so == 'Windows':

    sistema = 'win' + bits

    for paquete, dic_paq in info_paquetes.items():
        v = dic_paq['versión']
        dic_paq['formato_archivo'] = dic_paq['formato_archivo'].format(versión=v, v_py=versión_python, sis=sistema)

    instalar_requísitos()

"""
Ahora cosas normales de instalación.
"""

with open('tikon/versión.txt') as archivo_versión:
    versión = archivo_versión.read().strip()

setup(
    name='tikon',
    version=versión,
    packages=find_packages(),
    url='https://tikon.readthedocs.io',
    download_url='https://github.com/julienmalard/Tikon',
    license='GNU 3',
    author='Julien Jean Malard',
    author_email='julien.malard@mail.mcgill.ca',
    description='Modelos de redes agroecológicas',
    long_description='Tiko\'n es una herramienta para desarrollar modelos de agroecología (relaciones tróficas'
                     'entre insectos, enfermedades, y plantas). Está escrito para permitir la integración de modelos'
                     'de cultivos existentes.',
    requires=['pymc', 'numpy', 'matplotlib', 'scipy', 'SALib'],
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],
    package_data={
        # Incluir estos documentos de los paquetes:
        '': ['*.csv', 'versión.txt', '*.json', 'Interfaz/*.png', 'Interfaz/*.jpg', 'Interfaz/*.png'],
    },
)
