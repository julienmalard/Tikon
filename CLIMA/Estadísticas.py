import numpy as np
from scipy import stats as estad
import random
from pykrige.uk import UniversalKriging as krigUniversal


# Las funciones de Bahaa Khalil para generar datos que faltan
def move1(x, y):
    # Hirsch,R.M. (1982). A comparison of four streamflow record extension
    # techniques, Water Resources Research, 18, 1081 – 1088, 1982.
    x = np.array(x)
    y = np.array(y)
    r = np.correlate(y, x)

    b_move = np.nanstd(y) / np.nanstd(x)
    if r < 0:
        b_move *= -1
    a_move = np.nanmean(y) - (b_move * np.nanmean(x))
    return a_move[0], b_move[0]


def ktrl(x, y):
    # KTRL = Kendall-Theil Robust Line
    x = np.array(x)
    y = np.array(y)

    w = x.size()
    k = []
    for i in range(w-1, 1, -1):
        for j in range(0, i-2):
            yk = y[i]-y[j]
            xk = x[i]-x[j]
            k.append(yk / xk)

    k = np.array(k)
    b_ktrl = np.nanmedian(k)
    a_ktrl = np.nanmedian(y)-(b_ktrl*(np.nanmedian(x)))

    return a_ktrl[0], b_ktrl[0]


def ktrl2(x, y):
    # Modificacion del KTRL (KTRL2) desarrollado por Khalil et al (2012)
    # Khalil,B.,T.B.M.J.Ouarda,and A.St-Hilaire(2012). Comparison of
    # record-extension techniques water quality variables, Water Resources
    # Management, 26(14), 4259-4280.

    x = np.array(x)
    y = np.array(y)

    qx = np.percentile(x, [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95])
    qy = np.percentile(y, [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95])

    k2 = []
    for i in range(18, 1, -1):
        for j in range(0, i-2):
            yk2 = qy[i]-qy[j]
            xk2 = qx[i]-qx[j]
            k2.append(yk2/xk2)

    k2 = np.array(k2)
    b_ktrl2 = np.nanmedian(k2)
    a_ktrl2 = np.nanmedian(y)-(b_ktrl2*(np.nanmedian(x)))

    return a_ktrl2[0], b_ktrl2[0]


def rloc(x, y):
    # Robust Line of Organic Correlation (RLOC) desarrollado por Khalil and Adamowski (2012)

    # Khalil, B. and Adamowski, J. (2012). Record extension for short-gauged
    # water quality parameters using a newly proposed robust version of the line
    # of organic correlation technique, Hydrol. Earth Syst. Sci., 16, 2253-2266.

    x = np.array(x)
    y = np.array(y)

    r = np.correlate(y, x)

    qx = np.percentile(x, [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95])
    qy = np.percentile(y, [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95])

    b_rloc = (qy[14] - qy[4]) / (qx[14] - qx[4])
    if r < 0:
        b_rloc *= -1
    a_rloc = np.nanmedian(y)-(b_rloc*(np.nanmedian(x)))

    return a_rloc[0], b_rloc[0]


def reg_lin(x, y):
    x = np.array(x)
    y = np.array(y)
    pendiente, intersección = estad.linregress(x, y)[0:2]
    return intersección, pendiente


# Para verificar la presencia de valores atípicas
def verificar_atípicos(x, nivel=3.5):
    """
    Código modificado del código de Joe Kingston,
    http://stackoverflow.com/questions/22354094/pythonic-way-of-detecting-outliers-in-one-dimensional-observation-data
    """

    x = np.array(x)
    if len(x.shape) == 1:
        x = x[:, None]
    mediano = np.nanmedian(x, axis=0)
    dif = np.absolute(np.nansum((x - mediano), axis=-1))
    med_abs_deviation = np.nanmedian(dif)

    z_modificado = 0.6745 * dif / med_abs_deviation

    return (z_modificado > nivel).sum()


def eval_estaciones(var, lugar, cercanas, tipo):

    # Inicializar unos variables
    a_final = b_final = r2 = datos = None

    # Verificar para la presencia de valores atípicos
    atípicos = verificar_atípicos(lugar[var])
    for i in cercanas:
        atípicos = atípicos or verificar_atípicos(cercanas[i][var])

    # Asegurar tamaño igual para las listas de los datos
    X = []  # datos de la estación cercana
    Y = []  # datos de la estación de interés
    f = min(cercanas['Fecha'], lugar['Fecha'])
    while f <= max(cercanas['Fecha'], lugar['Fecha']):  # Para todas las fechas posibles
        if f in cercanas['Fecha']:  # Si hay datos de la estación cercana para la fecha
            X += cercanas[var][cercanas['Fecha'].index(f)]  # Añadir el dato a X
            if f in lugar['Fecha']:  # Si también existe el dato a la estación de interés...
                Y += lugar[var][lugar['Fecha'].index(f)]  # ...añadirlo a Y
            else:
                Y += float('NaN')  # Sino, poner un punto vacío para Y
        else:  # Si no hay datos de la estación cercana para la fecha...
            if f in lugar['Fecha']:  # ...pero sí hay datos en la estación de interés para la fecha
                X += float('NaN')  #
                Y += lugar[var][lugar['Fecha'].index(f)]
        f += 1

    # Una matriz de puntos para cuales hay datos en las dos estaciones
    completos = [(x, y) for x, y in zip(X, Y) if not np.isnan(x) and not np.isnan(y)]
    completos = np.array(list(zip(*completos)))  # Convertir a una matriz de numpy

    for otra_estación in cercanas:
        if tipo == 'puntual':
            if atípicos:
                a, b = ktrl(completos[0], completos[1])
            else:
                a, b = reg_lin(completos[0], completos[1])

            estimados = []
            verdaderos = []
            for j in range(100):  # Repetir 100 veces
                # Quitar al hazar el 10% de los datos disponibles (es decir, guardar 90%)
                a_quitar = random.sample(range(len(X)), round(len(X) * 0.10))
                conocidos_y = Y.copy()
                conocidos_x = X.copy()
                quitados_y = quitados_x = []
                for i in a_quitar:
                    quitados_x.append = conocidos_x.pop(i)
                    quitados_y.append = conocidos_y.pop(i)

                if atípicos:
                    a_estim, b_estim = ktrl(conocidos_x, conocidos_y)
                else:
                    a_estim, b_estim = reg_lin(conocidos_x, conocidos_y)

                estimados += a_estim + b_estim * quitados_x
                verdaderos += quitados_y

        elif tipo == 'extensa':
            if atípicos:
                a, b = ktrl2(completos[0], completos[1])
            else:
                a, b = move1(completos[0], completos[1])

            estimados = []
            verdaderos = []
            for j in range(100):  # Repetir 100 veces
                # Quitar al hazar el 10% de los datos disponibles (es decir, guardar 90%)
                inic = random.randint(0, len(X) - round(len(X) * 0.10))
                fin = inic + round(len(X) * 0.10)
                a_quitar = range(inic, fin)
                conocidos_y = Y.copy()
                conocidos_x = X.copy()
                quitados_y = quitados_x = []
                for i in a_quitar:
                    quitados_x.append = conocidos_x.pop(i)
                    quitados_y.append = conocidos_y.pop(i)

                if atípicos:
                    a_estim, b_estim = ktrl(conocidos_x, conocidos_y)
                else:
                    a_estim, b_estim = reg_lin(conocidos_x, conocidos_y)

                estimados += a_estim + b_estim * quitados_x
                verdaderos += quitados_y

        else:
            return False

        r2_nuevo = np.corrcoef(estimados, verdaderos) ** 2
        # Si es la primera estación posible a evaluar o si dió mejores resultados que la última estación:
        if not r2 or r2 < r2_nuevo:
            r2 = r2_nuevo
            a_final = a
            b_final = b
            datos = otra_estación  # Los datos de la estación escogida

    return a_final, b_final, datos


def krigear(lugar, cercanas, fecha_inic, fecha_fin):
    x = y = elev = []
    for estación in cercanas:
        x += estación['Coord'][0]
        y += estación['Coord'][1]
        elev += estación['Elev']

    for var in lugar['Datos']:
        f = fecha_inic
        while f <= fecha_fin:
            valor = []
            for estación in cercanas:
                valor += estación['Datos'][var][estación['Fecha'].index(f)]
            krigeaje = krigUniversal(x, y, valor, variogram_model='linear', drift_terms=['specified'],
                                     specified_drift=elev)
            lugar[var] = krigeaje.execute('points', lugar['Coord'][0], lugar['Coord'][1],
                                          specified_drift_arrays=lugar['Elev'])

            f += 1

    for var in lugar['Datos']:
        # Comprobar la incertidumbre
        predicciones = actuales = []
        for n, otra in enumerate(cercanas):
            estaciones_estim = cercanas.copy()
            estación_falta = estaciones_estim.pop(n)
            f = fecha_inic
            while f <= fecha_fin:
                valor = []
                for estación in estaciones_estim:
                    valor += estación[var][estación['Fecha'].index(f)]
                krigeaje = krigUniversal(x, y, valor, variogram_model='linear', drift_terms=['specified'],
                                         specified_drift=elev)
                predicciones += krigeaje.execute('points', estación_falta['Coord'][0], estación_falta['Coord'][1],
                                                 specified_drift_arrays=estación_falta['Elev'])
                actuales += estación_falta[var][estación_falta['Fecha'].index(f)]
                f += 1
        if var == 'Rad_sol' or var == 'Precip':

            incert[var] = 'N~(%s, %s)' % (lugar[var] * error, 4)
    return lugar, incert
