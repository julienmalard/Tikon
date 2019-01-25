from setuptools import setup, find_packages


def leer(arch):
    with open(arch, 'r', encoding='utf-8') as d:
        return d.read()


setup(
    name='tikon',
    version=leer('tikon/versión.txt').strip(),
    packages=find_packages(),
    url='https://tikon.readthedocs.io',
    download_url='https://github.com/julienmalard/Tikon',
    license='GNU 3',
    author='Julien Jean Malard',
    author_email='julien.malard@mail.mcgill.ca',
    description='Modelos de redes agroecológicas',
    long_description=leer('README.md'),
    install_requires=['numpy', 'matplotlib', 'scipy', 'SALib', 'spotpy', 'chardet', 'pandas', 'taqdir'],
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
