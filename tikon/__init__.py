import numpy as np

from pkg_resources import resource_filename

with open(resource_filename('tikon', 'versión.txt')) as archivo_versión:
    __versión__ = __version__ = archivo_versión.read().strip()

# Numpy nos da un montón de errores que no nos importan en Tiko'n.
np.warnings.filterwarnings('ignore')

__autor__ = 'Julien Malard'
__correo__ = 'julien.malard@mail.mcgill.ca'
