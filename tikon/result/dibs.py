import os

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura
from tikon.result.utils import EJE_TIEMPO, EJE_PARÁMS, EJE_ESTOC


def graficar_res(
        título, directorio, simulado, obs=None, color='#99CC00', promedio=True, incert='confianza',
        etiq_x=None
):
    etiq_x = 'fecha' if etiq_x is None else etiq_x
    if not os.path.isdir(directorio):
        os.makedirs(directorio)

    fig = Figura()
    TelaFigura(fig)
    ejes = fig.add_subplot(111)

    # El vector de días
    x = simulado[EJE_TIEMPO]

    # Si necesario, incluir el promedio de todas las repeticiones (estocásticas y paramétricas)
    prom_simul = simulado.mean(dim=(EJE_ESTOC, EJE_PARÁMS))
    if promedio:
        ejes.plot(x, prom_simul, lw=2, color=color, label='Promedio')

    # Si hay observaciones, mostrarlas también
    if obs is not None:
        ejes.plot(obs[EJE_TIEMPO], obs, 'o', color=color, label='Observaciones')
        ejes.plot(obs[EJE_TIEMPO], obs, lw=1, color='#000000')

    # Incluir el incertidumbre si necesario
    if incert is None:
        # Si no quiso el usuario, no poner el incertidumbre
        pass

    elif incert == 'confianza':
        # Mostrar el nivel de confianza en la incertidumbre

        # Los niveles de confianza para mostrar
        centiles = [.50, .75, .95, .99]

        # Mínimo y máximo del percentil anterior
        máx_perc_ant = mín_perc_ant = simulado.median(dim=(EJE_ESTOC, EJE_PARÁMS))

        # Para cada percentil...
        for n, p in enumerate(centiles):
            # Percentiles máximos y mínimos
            máx_perc = prom_simul.quantile(0.50 + p / 2, dim=(EJE_ESTOC, EJE_PARÁMS))
            mín_perc = prom_simul.quantile((1 - p) / 2, dim=(EJE_ESTOC, EJE_PARÁMS))

            # Calcular el % de opacidad y dibujar
            op_máx = 0.6
            op_mín = 0.2
            opacidad = (1 - n / (len(centiles) - 1)) * (op_máx - op_mín) + op_mín

            ejes.fill_between(
                x, máx_perc_ant, máx_perc,
                facecolor=color, alpha=opacidad, linewidth=0.5, edgecolor=color, label='IC {} %'.format(p)
            )
            ejes.fill_between(
                x, mín_perc, mín_perc_ant,
                facecolor=color, alpha=opacidad, linewidth=0.5, edgecolor=color
            )

            # Guardar los máximos y mínimos
            mín_perc_ant = mín_perc
            máx_perc_ant = máx_perc

    elif incert == 'componentes':
        # Mostrar la incertidumbre descompuesta por sus fuentes

        # El rango total de las simulaciones
        máx_total = prom_simul.max(dim=(EJE_ESTOC, EJE_PARÁMS))
        mín_total = prom_simul.min(dim=(EJE_ESTOC, EJE_PARÁMS))
        rango_total = máx_total - mín_total

        # La desviación estándar de todas las simulaciones (incertidumbre total)
        des_est_total = prom_simul.std(dim=(EJE_ESTOC, EJE_PARÁMS))

        # El incertidumbre estocástico promedio
        des_est_estóc = prom_simul.std(dim=EJE_ESTOC).mean(dim=EJE_PARÁMS)

        # Inferir el incertidumbre paramétrico
        des_est_parám = des_est_total - des_est_estóc
        frac_des_est_parám = (des_est_parám / des_est_total).fillna(0)
        incert_parám = rango_total * frac_des_est_parám

        # Límites de la región de incertidumbre paramétrica en el gráfico
        mín_parám = np.maximum(mín_total, prom_simul - incert_parám / 2)
        máx_parám = mín_parám + incert_parám

        ejes.fill_between(x, máx_parám, mín_parám, facecolor=color, alpha=0.5, label='Incert paramétrico')

        ejes.fill_between(x, máx_total, mín_total, facecolor=color, alpha=0.3, label='Incert estocástico')

    else:
        raise ValueError('`incert` debe ser "componentes" o "confianza", no  "%s".' % incert)

    ejes.set_xlabel(etiq_x)
    ejes.set_ylabel(etiq_y)
    ejes.set_title(título)

    ejes.legend(loc=2)

    if os.path.splitext(directorio)[1] != '.jpg':
        directorio = os.path.join(directorio, título + '.jpg')
    fig.savefig(directorio)