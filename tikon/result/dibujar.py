import os

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura


def graficar_pred(
        título, directorio, matr_predic, vector_obs=None, t_pred=None, t_obs=None,
        etiq_y='', etiq_x='Día', color='#99CC00', promedio=True, incert='componentes'
):
    """"""
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

    e_t, e_estoc, e_parám = (0, 1, 2)
    if not os.path.isdir(directorio):
        os.makedirs(directorio)

    fig = Figura()
    TelaFigura(fig)
    ejes = fig.add_subplot(111)

    # El vector de días
    if t_pred is None:
        x = np.arange(matr_predic.shape[e_t])
    else:
        x = t_pred

    # Si necesario, incluir el promedio de todas las repeticiones (estocásticas y paramétricas)
    prom_predic = matr_predic.mean(axis=(e_estoc, e_parám))
    if promedio:
        ejes.plot(x, prom_predic, lw=2, color=color)

    # Si hay observaciones, mostrarlas también
    if vector_obs is not None:
        if t_obs is None:
            t_obs = np.arange(len(vector_obs))

        disp = np.where(~np.isnan(vector_obs))
        t_obs = t_obs[disp]
        vector_obs = vector_obs[disp]

        ejes.plot(t_obs, vector_obs, 'o', color=color, label='Observaciones')
        ejes.plot(t_obs, vector_obs, lw=1, color='#000000')

    # Incluir el incertidumbre
    if incert is None:
        # Si no quiso el usuario, no poner la incertidumbre
        pass

    elif incert == 'confianza':
        # Mostrar el nivel de confianza en la incertidumbre

        # Los niveles de confianza para mostrar
        percentiles = [50, 75, 95, 99, 100]
        percentiles.sort()

        # Mínimo y máximo del percentil anterior
        máx_perc_ant = mín_perc_ant = prom_predic

        # Para cada percentil...
        for n, p in enumerate(percentiles):
            # Percentiles máximos y mínimos
            máx_perc = np.percentile(matr_predic, 50 + p / 2, axis=(e_estoc, e_parám))
            mín_perc = np.percentile(matr_predic, (100 - p) / 2, axis=(e_estoc, e_parám))

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
        máx_total = matr_predic.max(axis=(e_estoc, e_parám))
        mín_total = matr_predic.min(axis=(e_estoc, e_parám))
        rango_total = np.subtract(máx_total, mín_total)

        # La desviación estándar de todas las simulaciones (incertidumbre total)
        des_est_total = np.std(matr_predic, axis=(e_estoc, e_parám))

        # El incertidumbre estocástico promedio
        des_est_estóc = np.mean(
            np.std(matr_predic, axis=e_estoc),
            axis=e_parám if e_parám < e_estoc else e_parám - 1
        )

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
        raise ValueError('``incertidumbre`` debe ser "componentes" o "confianza", no  "%s".' % incert)

    ejes.set_xlabel(etiq_x)
    ejes.set_ylabel(etiq_y)
    ejes.set_title(título)

    ejes.legend(loc=2)

    if directorio[-4:] != '.png':
        válidos = (' ', '.', '_')
        nombre_arch = "".join(c for c in (título + '.png') if c.isalnum() or c in válidos).rstrip()
        directorio = os.path.join(directorio, nombre_arch)
    fig.savefig(directorio)
