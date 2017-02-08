from setuptools import setup, find_packages


with open('tikon/versión.txt') as archivo_versión:
    versión = archivo_versión.read().strip()

setup(
    name='tikon',
    version=versión,
    packages=find_packages(),
    url='https://github.com/julienmalard/Tikon',
    license='GNU 3',
    author='Julien Jean Malard',
    author_email='julien.malard@mail.mcgill.ca',
    description='Modelos de redes agroecológicas',
    requires=['pymc', 'numpy', 'matplotlib', 'scipy'],
    package_data={
        # Incluir estos documentos de los paquetes:
        '': ['*.csv', 'versión.txt', 'Interfaz/*.json', 'Interfaz/*.png', 'Interfaz/*.jpg', 'Interfaz/*.png'],
    },
)
