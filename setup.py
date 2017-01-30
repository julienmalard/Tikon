from setuptools import setup, find_packages


with open('tikon/versión.txt') as archivo_versión:
    versión = archivo_versión.read().strip()

setup(
    name='Tinamit',
    version=versión,
    packages=find_packages(),
    url='https://github.com/julienmalard/Tikon',
    license='GNU 3',
    author='Julien Jean Malard',
    author_email='julien.malard@mail.mcgill.ca',
    description='',
    requires=['pymc', 'numpy', 'matplotlib', 'scipy'],
    package_data={
        # Incluir estos documentos de los paquetes:
        '': ['*.csv', 'Interfaz/*.json', 'Interfaz/*.png', 'Interfaz/*.jpg', 'Interfaz/*.png'],
    },
)
