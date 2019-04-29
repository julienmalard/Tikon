import os

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura


def graficar_pred(
        título, directorio, matr_predic, vector_obs=None, t_pred=None, t_obs=None,
        etiq_y='', etiq_x='Día', color='#99CC00', promedio=True, incert='confianza'
):
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
        máx_perc_ant = mín_perc_ant = np.median(matr_predic, axis=(e_estoc, e_parám))

        # Para cada percentil...
        for n, p in enumerate(percentiles):
            # Percentiles máximos y mínimos
            máx_perc = np.percentile(matr_predic, 50 + p / 2, axis=(e_estoc, e_parám))
            mín_perc = np.percentile(matr_predic, (100 - p) / 2, axis=(e_estoc, e_parám))

            # Calcular el % de opacidad y dibujar
            op_máx = 0.5
            op_mín = 0.01
            opacidad = (1 - n / (len(percentiles) - 1)) * (op_máx - op_mín) + op_mín

            ejes.fill_between(
                x, máx_perc_ant, máx_perc,
                facecolor=color, alpha=opacidad, linewidth=0.5, edgecolor=color, label='IC {} %'.format(p)
            )
            ejes.fill_between(
                x, mín_perc, mín_perc_ant,
                facecolor=color, alpha=opacidad, linewidth=0.5, edgecolor=color, label='IC {} %'.format(p)
            )

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
        frac_des_est_parám[np.isnan(frac_des_est_parám)] = 0
        incert_parám = np.multiply(rango_total, frac_des_est_parám)

        # Límites de la región de incertidumbre paramétrica en el gráfico
        mín_parám = np.maximum(mín_total, prom_predic - np.divide(incert_parám, 2))
        máx_parám = mín_parám + incert_parám

        ejes.fill_between(x, máx_parám, mín_parám, facecolor=color, alpha=0.5, label='Incert paramétrico')

        ejes.fill_between(x, máx_total, mín_total, facecolor=color, alpha=0.3, label='Incert estocástico')

    else:
        raise ValueError('``incertidumbre`` debe ser "componentes" o "confianza", no  "%s".' % incert)

    ejes.set_xlabel(etiq_x)
    ejes.set_ylabel(etiq_y)
    ejes.set_title(título)

    ejes.legend(loc=2)

    if os.path.splitext(directorio)[1] != '.png':
        directorio = os.path.join(directorio, título + '.png')
    fig.savefig(directorio)
