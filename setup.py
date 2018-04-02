from setuptools import setup, find_packages


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
    install_requires=['pymc', 'numpy', 'matplotlib', 'scipy', 'SALib', 'pathvalidate', 'pymc3', 'theano'],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
    ],
    package_data={
        # Incluir estos documentos de los paquetes:
        '': ['*.csv', 'versión.txt', '*.json', 'Interfaz/*.png', 'Interfaz/*.jpg'],
    },
)
