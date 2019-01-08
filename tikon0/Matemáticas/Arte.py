import os

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura

from tikon0.Controles import valid_archivo
from tikon0.Matemáticas.Variables import VarSciPy, VarSpotPy


def graficar_línea(datos, título, etiq_y=None, etiq_x='Día', color=None, directorio=None):
    """

    :param datos:
    :type datos: np.ndarray
    :param título:
    :type título: str
    :param etiq_y:
    :type etiq_y: str
    :param etiq_x:
    :type etiq_x: str
    :param color:
    :type color: str
    :param directorio:
    :type directorio: str

    """

    if color is None:
        color = '#99CC00'

    if etiq_y is None:
        etiq_y = título

    if directorio is None:
        raise ValueError('Hay que especificar un archivo para guardar el gráfico de %s.' % título)
    elif not os.path.isdir(directorio):
        os.makedirs(directorio)

    # El vector de días
    x = np.arange(datos.shape[0])

    # Dibujar la línea
    fig = Figura()
    TelaFigura(fig)
    ejes = fig.add_subplot(111)
    ejes.set_aspect('equal')

    ejes.plot(x, datos, lw=2, color=color)

    ejes.set_xlabel(etiq_x)
    ejes.set_ylabel(etiq_y)
    ejes.set_title(título)

    ejes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)

    if directorio[-4:] != '.png':
        válidos = (' ', '.', '_')
        nombre_arch = "".join(c for c in (título + '.png') if c.isalnum() or c in válidos).rstrip()
        directorio = os.path.join(directorio, nombre_arch)
    fig.savefig(directorio)


def graficar_dists(dists, valores=None, rango=None, título=None, archivo=None):
    """
    Esta función genera un gráfico de una o más distribuciones y valores.

    :param dists: Una lista de las distribuciones para graficar.
    :type dists: list[str, VarCalib] | str | VarCalib

    :param valores: Una matriz numpy de valores para generar un histograma (opcional)
    :type valores: np.ndarray

    :param rango: Un rango de valores para resaltar en el gráfico (opcional).
    :type rango: tuple

    :param título: El título del gráfico, si hay.
    :type título: str

    :param archivo: Dónde hay que guardar el dibujo. Si no se especifica, se presentará el gráfico al usuario en una
      nueva ventana (y el programa esperará que la usadora cierra la ventana antes de seguir con su ejecución).
    :type archivo: str

    """

    if type(dists) is not list:
        dists = [dists]

    n = 100000

    fig = Figura()
    TelaFigura(fig)

    # Poner cada distribución en el gráfico
    for dist in dists:

        if isinstance(dist, VarSpotPy):
            ejes = fig.subplots(1, 2)

            dist.dibujar(ejes=ejes)

            # Si se especificó un título, ponerlo
            if título is not None:
                fig.suptitle(título)

        else:

            if isinstance(dist, str):
                dist = VarSciPy.de_texto(texto=dist)

            if isinstance(dist, VarSciPy):
                x = np.linspace(dist.percentiles(0.01), dist.percentiles(0.99), n)
                y = dist.fdp(x)
            else:
                raise TypeError('El tipo de distribución "%s" no se reconoce como distribución aceptada.' % type(dist))

            ejes = fig.add_subplot(111)

            # Dibujar la distribución
            ejes.plot(x, y, 'b-', lw=2, alpha=0.6)

            # Resaltar un rango, si necesario
            if rango is not None:
                if rango[1] < rango[0]:
                    rango = (rango[1], rango[0])
                ejes.fill_between(x[(rango[0] <= x) & (x <= rango[1])], 0, y[(rango[0] <= x) & (x <= rango[1])],
                                  color='blue', alpha=0.2)

            # Si hay valores, hacer un histrograma
            if valores is not None:
                valores = valores.astype(float)
                ejes.hist(valores, density=True, color='green', histtype='stepfilled', alpha=0.2)

            # Si se especificó un título, ponerlo
            if título is not None:
                ejes.set_title(título)

    # Guardar el gráfico
    if archivo[-4:] != '.png':
        archivo = os.path.join(archivo, título + '.png')

    valid_archivo(archivo)

    fig.savefig(archivo)
