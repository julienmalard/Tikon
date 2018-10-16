import os

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura

from tikon.Matemáticas.Variables import VarSciPy, VarSpotPy
from tikon.Controles import valid_archivo


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


def graficar_pred(matr_predic, título, vector_obs=None, tiempos_obs=None, etiq_y=None, etiq_x='Día', color=None,
                  promedio=True, incert='componentes', n_líneas=0, directorio=None):
    """
    Esta función genera un gráfico, dato una matriz de predicciones y un vector de observaciones temporales.

    :param matr_predic: La matriz de predicciones. Eje 0 = incertidumbre estocástico, eje 1 = incertidumbre
    paramétrico, eje 2 = día.
    :type matr_predic: np.ndarray

    :param vector_obs: El vector de las observaciones. Eje 0 = tiempo.
    :type vector_obs: np.ndarray | None

    :param tiempos_obs: El vector de los tiempos de las observaciones.
    :type tiempos_obs: np.ndarray

    :param título: El título del gráfico
    :type título: str

    :param etiq_y: La etiqueta para el eje y del gráfico.
    :type etiq_y: str

    :param etiq_x: La etiqueta para el eje x del gráfico
    :type etiq_x: str

    :param color: El color para el gráfico
    :type color: str

    :param promedio: Si hay que mostrar el promedio de las repeticiones o no.
    :type promedio: bool

    :param incert: El tipo de incertidumbre para mostrar (o no). Puede ser None, 'confianza', o 'descomponer'.
    :type incert: str | None

    :param n_líneas: El número de líneas de repeticiones para mostrar.
    :type n_líneas: int

    :param directorio: El archivo donde guardar el gráfico
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

    fig = Figura()
    TelaFigura(fig)
    ejes = fig.add_subplot(111)

    # El vector de días
    x = np.arange(matr_predic.shape[2])

    # Si necesario, incluir el promedio de todas las repeticiones (estocásticas y paramétricas)
    prom_predic = matr_predic.mean(axis=(0, 1))
    if promedio:
        ejes.plot(x, prom_predic, lw=2, color=color)

    # Si hay observaciones, mostrarlas también
    if vector_obs is not None:
        if tiempos_obs is None:
            tiempos_obs = np.arange(len(vector_obs))

        vacíos = np.where(~np.isnan(vector_obs))
        tiempos_obs = tiempos_obs[vacíos]
        vector_obs = vector_obs[vacíos]

        ejes.plot(tiempos_obs, vector_obs, 'o', color=color, label='Obs')
        ejes.plot(tiempos_obs, vector_obs, lw=1, color='#000000')

    # Incluir el incertidumbre
    if incert is None:
        # Si no quiso el usuario, no poner la incertidumbre
        pass

    elif incert == 'confianza':
        # Mostrar el nivel de confianza en la incertidumbre

        # Los niveles de confianza a mostrar
        percentiles = [50, 75, 95, 99, 100]
        percentiles.sort()

        # Mínimo y máximo del percentil anterior
        máx_perc_ant = mín_perc_ant = prom_predic

        # Para cada percentil...
        for n, p in enumerate(percentiles):
            # Percentiles máximos y mínimos
            máx_perc = np.percentile(matr_predic, 50 + p / 2, axis=(0, 1))
            mín_perc = np.percentile(matr_predic, (100 - p) / 2, axis=(0, 1))

            # Calcular el % de opacidad y dibujar
            op_máx = 0.5
            op_mín = 0.01
            opacidad = (1 - n / (len(percentiles) - 1)) * (op_máx - op_mín) + op_mín

            ejes.fill_between(x, máx_perc_ant, máx_perc,
                              facecolor=color, alpha=opacidad, linewidth=0.5, edgecolor=color)
            ejes.fill_between(x, mín_perc, mín_perc_ant,
                              facecolor=color, alpha=opacidad, linewidth=0.5, edgecolor=color)

            # Guardar los máximos y mínimos
            mín_perc_ant = mín_perc
            máx_perc_ant = máx_perc

    elif incert == 'componentes':
        # Mostrar la incertidumbre descompuesta por sus fuentes

        # El rango total de las simulaciones
        máx_total = matr_predic.max(axis=(0, 1))
        mín_total = matr_predic.min(axis=(0, 1))
        rango_total = np.subtract(máx_total, mín_total)

        # La desviación estándar de todas las simulaciones (incertidumbre total)
        des_est_total = np.std(matr_predic, axis=(0, 1))

        # El incertidumbre estocástico promedio
        des_est_estóc = np.mean(np.std(matr_predic, axis=0), axis=0)

        # Inferir el incertidumbre paramétrico
        des_est_parám = np.subtract(des_est_total, des_est_estóc)
        frac_des_est_parám = np.divide(des_est_parám, des_est_total)
        incert_parám = np.multiply(rango_total, frac_des_est_parám)

        # Límites de la región de incertidumbre paramétrica en el gráfico
        mitad = np.divide(np.add(máx_total, mín_total), 2)
        máx_parám = np.add(mitad, np.divide(incert_parám, 2))
        mín_parám = np.subtract(mitad, np.divide(incert_parám, 2))

        ejes.fill_between(x, máx_parám, mín_parám, facecolor=color, alpha=0.5, label='Incert paramétrico')

        ejes.fill_between(x, máx_total, mín_total, facecolor=color, alpha=0.3, label='Incert estocástico')

    else:
        raise ValueError('No entiendo el tipo de incertidumbre "%s" que especificaste para el gráfico.' % incert)

    # Si lo especificó el usuario, mostrar las líneas de algunas repeticiones.
    if n_líneas > 0:
        n_rep_estoc = matr_predic.shape[0]
        n_rep_parám = matr_predic.shape[1]
        rep_total = n_rep_estoc * n_rep_parám

        if n_líneas > rep_total:
            n_líneas = rep_total

        í_líneas = np.random.randint(rep_total, size=n_líneas)
        í_lín_estoc = np.floor_divide(í_líneas, n_rep_estoc)
        í_lín_parám = np.remainder(í_líneas, n_rep_parám)

        for n in range(í_lín_estoc.shape[0]):
            ejes.plot(x, matr_predic[í_lín_estoc[n], í_lín_parám[n]], lw=1, color=color)

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

        if isinstance(dist, VarCalib):
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
                ejes.hist(valores, normed=True, color='green', histtype='stepfilled', alpha=0.2)

            # Si se especificó un título, ponerlo
            if título is not None:
                ejes.set_title(título)

    # Guardar el gráfico
    if archivo[-4:] != '.png':
        archivo = os.path.join(archivo, título + '.png')

    valid_archivo(archivo)

    fig.savefig(archivo)
