from distutils.core import setup

setup(
    name='Tinamit',
    version='1.0.0',
    packages=['', 'RAE', 'CLIMA', 'CLIMA.PyKrige', 'CULTIVO', 'CULTIVO.MODELOS_EXTERNOS.DSSAT', 'Matemáticas'],
    url='https://github.com/julienmalard/Tikon',
    license='GNU 3',
    author='Julien Jean Malard',
    author_email='julien.malard@mail.mcgill.ca',
    description='',
    requires=['pymc', 'numpy', 'matplotlib', 'scipy']
)
