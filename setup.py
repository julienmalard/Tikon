from setuptools import setup, find_packages

setup(
    name='Tinamit',
    version='1.0.0',
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
