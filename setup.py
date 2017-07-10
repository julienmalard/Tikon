import os
import platform
import sys
from subprocess import run
import urllib.request
import shutil
from setuptools import setup, find_packages
from warnings import warn as avisar

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

directorio = os.path.split(os.path.realpath(__file__))[0]

directorio_móds = os.path.join(directorio, 'Módulos')

if not os.path.exists(directorio_móds):
    os.makedirs(directorio_móds)

directorio_python = os.path.split(sys.executable)[0]

versión_python = str(sys.version_info.major) + str(sys.version_info.minor)

info_paquetes = {'numpy': {'versión': '1.11.3',
                           'formato_archivo': 'numpy-{versión}+mkl-cp{v_py}-cp{v_py}m-{sis}.whl',
                           'id_dropbox': {'32': 'rmsmiu1ivpnvizd/numpy-1.11.3%2Bmkl-cp36-cp36m-win32.whl?dl=1',
                                          '64': None}
                           },
                 'scipy': {'versión': '0.18.1',
                           'formato_archivo': 'scipy-{versión}-cp{v_py}-none-{sis}.whl',
                           'id_google': {'32': '0B8RjC9bwyAOwTEZCdWdMbDQ4VG8',
                                         '64': None}
                           },
                 'matplotlib': {'versión': '2.0.0',
                                'formato_archivo': 'matplotlib-{versión}-cp{v_py}-none-{sis}.whl',
                                'id_google': {'32': '0B8RjC9bwyAOwRDlIU2x1YlY0U1U',
                                              '64': None}
                                },
                 'pymc': {'versión': '2.3.6',
                          'formato_archivo': 'pymc-{versión}-cp{v_py}-none-{sis}.whl',
                          'id_google': {'32': '0B8RjC9bwyAOwTXlFQjZVYWczUTA',
                                        '64': None}
                          },
                 }

so = platform.system()


def _actualizar_pip():
    print('Actualizando pip...')
    comanda_pip = '%s install --upgrade pip' % (os.path.join(directorio_python, 'Scripts', 'pip'))
    run(comanda_pip)


def _descargar_whl(nombre):
    print('Descargando paquete "{}"...'.format(nombre))
    llave = url = None

    repositorios = {'id_google': 'https://drive.google.com/uc?export=download&id={}',
                    'id_dropbox': 'https://www.dropbox.com/s/{}'}

    for r, u in repositorios.items():
        try:
            llave = info_paquetes[nombre][r][bits]  # type: str
        except KeyError:
            pass
        if llave is not None:
            url = u.format(llave)
            break

    if url is None:
        avisar('No existe descarga para paquete {} en {} bits.'.format(nombre, bits))

    nombre_archivo = info_paquetes[nombre]['formato_archivo']
    urllib.request.urlretrieve(url, os.path.join(directorio_móds, nombre_archivo))


def _instalar_whl(nombre):
    nombre_archivo = info_paquetes[nombre]['formato_archivo']

    if not os.path.isfile(os.path.join(directorio_móds, nombre_archivo)):
        _descargar_whl(nombre)

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
        # Actualizar Pip
        _actualizar_pip()

        # Instalar cada paquete necesario
        for paq in lista_paquetes:
            _instalar_whl(paq)

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
    bits = platform.architecture()[0][:2]
    sistema = 'win' + bits

    for paquete, dic_paq in info_paquetes.items():
        v = dic_paq['versión']
        dic_paq['formato_archivo'] = dic_paq['formato_archivo'].format(versión=v, v_py=versión_python, sis=sistema)

    instalar_requísitos()


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
                     'entre insectos, enfermedades, y plantas. Está escrito para permitir la integración de modelos'
                     'de cultivos existentes.',
    requires=['pymc', 'numpy', 'matplotlib', 'scipy'],
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],
    package_data={
        # Incluir estos documentos de los paquetes:
        '': ['*.csv', 'versión.txt', '*.json', 'Interfaz/*.png', 'Interfaz/*.jpg', 'Interfaz/*.png'],
    },
)
