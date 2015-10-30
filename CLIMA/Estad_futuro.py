import random as aleatorio
import math as mat
import numpy as np
import datetime as ft
import calendar as calendario

'''
Este módulo contiene las funciones necesarias para convertir datos de clima mensuales (incluso predicciones
climáticas) en datos de clima diarios realísticos.
Se base en mayor parte en el módulo WGEN de DSSAT.
'''


# Para generar datos diarios
def generarmeteo(dic, fecha_inic, fecha_fin):
    parám = {}
    lat = dic['Lat']

    # Centrar las observaciones de parámetros alrededor del medio de cada mes
    for mes in dic['Mes']:
        if mes.day == 1:
            día_mes = calendario.monthrange(mes.year, mes.mes)
            mes.replace(day=round(día_mes/2))

    parám['Mes'] = meses = dic['Mes']

    if fecha_inic < meses[0] or fecha_fin > meses[-1].replace(day=calendario.monthrange(meses[-1].year,
                                                                                        meses[-1].month)):
        return 'Error: Faltan datos de clima mensuales para generar datos diario en el plazo especificado.'

    # Verificar si tenemos los parámetros requísitos para WGEN:
    paráms_wgen = True
    for p in ['Prom_rad_dia_seco_mens', 'Varia_rad_dia_seco_mens', 'Prom_rad_dia_lluv_mens', 'Varia_rad_dia_lluv_mens',
              'Prom_temp_dia_seco_mens', 'Varia_temp_dia_seco_mens', 'Prom_temp_dia_lluv_mens',
              'Varia_temp_dia_lluv_mens', 'Tdía_mín_prom_mens', 'Varia_temp_dia_min_prom']:
        if len(dic[p]) == len(meses):
            parám[p] = dic[p]
        else:
            paráms_wgen = False

    # Guardar el resto de los parámetros:
    for p in ['Rad_prom_mens', 'Tdia_máx_prom_mens', 'Prec_total_prom_mens',
              'Prom_días_prec_mens', 'Horas_sol_dia_prom_mens', 'Intercept_angstrom_mens',
              'Multiplicador_angstrom_mens']:
        parám[p] = dic[p]

    if paráms_wgen:  # Si los tenemos...
        parám = wgenparám(parám, fecha_inic, fecha_fin)

    else:  # Si tenemos que generarlos por simmeteo:
        parám = simmeteogenparám(parám, lat, fecha_inic, fecha_fin)

    generados = generar(parám, lat, fecha_inic, fecha_fin)

    return generados


def wgenparám(parám, fecha_inic, fecha_fin):
    meses = parám['Mes']
    inic = meses.index(ft.date(fecha_inic.year, fecha_inic.month, 1))
    fin = meses.index(ft.date(fecha_fin.year, fecha_fin.month + 1, 1) - ft.timedelta(1))
    for p in parám:
        parám[p] = parám[p][inic-1:fin+2]
    alpha_distgamma_prec = parám['Alpha_distgamma_prec']
    prec_total_prom_mens = parám['Prec_total_prom_mens']
    prob_lluv_después_seco = parám['Prob_lluv_después_seco']
    prom_días_prec_mens = parám['Prom_días_prec_mens']

    prob_lluv_después_lluv = parám['Prob_lluv_después_lluv'] = []
    beta_distgamma_prec = parám['Beta_distgamma_prec'] = []
    for mes in range(inic, fin+1):
        if abs(prom_días_prec_mens) < 1E-4 or abs(prec_total_prom_mens) < 1E-4:
            prob_lluv_después_seco.append(0)
            prob_lluv_después_lluv.append(0)
            alpha_distgamma_prec.append(0.44)
            beta_distgamma_prec.append(0)
        else:
            núm_días = calendario.monthrange(fecha_inic.year + mat.floor(mes/12), mes % 12 + 1)[1]
            prob_lluv = prom_días_prec_mens[mes]/núm_días
            prob_lluv_después_lluv.append(1 - prob_lluv_después_seco * (1-prob_lluv)/prob_lluv)
            prob_lluv_después_lluv.append(min(max(prob_lluv_después_lluv[mes], 0), 1))
            alpha_distgamma_prec.append(min(max(alpha_distgamma_prec[mes], 0.01), 0.998))
            prom_precip_día_lluv = prec_total_prom_mens[mes]/prom_días_prec_mens[mes]
            beta_distgamma_prec.append(max(prom_precip_día_lluv/alpha_distgamma_prec[mes], 0))

    return parám


# Generador SIMMETEO
def simmeteogenparám(parám, lat, fecha_inic, fecha_fin):
    meses = parám['Mes']
    inic = meses.index(ft.date(fecha_inic.year, fecha_inic.month, 1))
    fin = meses.index(ft.date(fecha_fin.year, fecha_fin.month + 1, 1) - ft.timedelta(1))
    for p in parám:
        parám[p] = parám[p][inic-1:fin+1]

    rad_prom_mens = parám['Rad_prom_mens']
    tdía_máx_prom_mens = parám['Tdía_máx_prom_mens']
    tdía_mín_prom_mens = parám['Tdía_mín_prom_mens']
    prec_total_prom_mens = parám['Prec_total_prom_mens']
    prom_días_prec_mens = parám['Prom_días_prec_mens']
    alpha_distgamma_prec = []
    prob_lluv_después_seco = []
    prob_lluv = []
    prob_lluv_después_lluv = parám['Prob_lluv_después_lluv'] = []
    beta_distgamma_prec = parám['Beta_distgamma_prec'] = []

    for mes in range(inic, fin+1):
        if abs(prom_días_prec_mens) < 1E-4 or abs(prec_total_prom_mens) < 1E-4:
            prob_lluv.append(0)
            prob_lluv_después_seco.append(0)
            prob_lluv_después_lluv.append(0)
            alpha_distgamma_prec.append(0.44)
            beta_distgamma_prec.append(0)
        else:
            núm_días = calendario.monthrange(fecha_inic.year + mat.floor(mes/12), mes % 12 + 1)[1]
            prob_lluv.append(prom_días_prec_mens / núm_días)
            prob_lluv_después_seco.append(0.75 * prob_lluv)
            temp = 1 - prob_lluv_después_seco[-1] * (1 - prob_lluv[-1])/prob_lluv[-1]
            prob_lluv_después_lluv.append(min(max(temp, 0), 1))
            prom_precip_día_lluv = prec_total_prom_mens / prom_días_prec_mens
            beta_distgamma_prec.append(max(-2.16 + 1.83 * prom_precip_día_lluv, 0.01))
            alpha_distgamma_prec.append(min(max(prom_precip_día_lluv/beta_distgamma_prec, 0.01), 0.998))

    prom_prob_lluv = np.average(prob_lluv)
    prom_prob_lluv_después_seco = np.average(prob_lluv_después_seco)

    fourier_rad_prom_mens = fourcf(rad_prom_mens)
    savg = 23.87 * fourier_rad_prom_mens[0]
    sdiff = abs(410. - 3.21 * lat - 0.350 * savg)
    fourier_prom_rad_dia_seco_mens = np.zeros(3)
    fourier_prom_rad_dia_seco_mens[0] = (savg+prom_prob_lluv*sdiff) * 0.04189
    fourier_prom_rad_dia_seco_mens[1] = fourier_rad_prom_mens[1]
    fourier_prom_rad_dia_seco_mens[2] = fourier_rad_prom_mens[2]

    fourier_prom_rad_dia_lluv_mens = np.zeros(3)
    fourier_prom_rad_dia_lluv_mens[0] = (savg-(1.0-prom_prob_lluv)*sdiff) * 0.04189
    fourier_prom_rad_dia_lluv_mens[1] = fourier_rad_prom_mens[1]
    fourier_prom_rad_dia_lluv_mens[2] = fourier_rad_prom_mens[2]

    srdcvf = np.zeros(3)
    srdcvf[0] = 0.24
    srdcvf[1] = -0.08
    srdcvf[2] = fourier_rad_prom_mens[2]

    srwcvf = np.zeros(3)
    srwcvf[0] = 0.48
    srwcvf[1] = -0.13
    srwcvf[2] = fourier_rad_prom_mens[2]

    fourier_tdía_máx_prom_mens = fourcf(tdía_máx_prom_mens)
    tdiff = abs(9.67-27.4 * prom_prob_lluv_después_seco) * 5/9
    fourier_prom_temp_dia_seco_mens = np.zeros(3)
    fourier_prom_temp_dia_seco_mens[0] = fourier_tdía_máx_prom_mens[0] + prom_prob_lluv*tdiff
    fourier_prom_temp_dia_seco_mens[1] = fourier_tdía_máx_prom_mens[1]
    fourier_prom_temp_dia_seco_mens[2] = fourier_tdía_máx_prom_mens[2]

    fourier_prom_temp_dia_lluv_mens = np.zeros(3)
    fourier_prom_temp_dia_lluv_mens[0] = fourier_tdía_máx_prom_mens[0] - (1.-prom_prob_lluv)*tdiff
    fourier_prom_temp_dia_lluv_mens[1] = fourier_tdía_máx_prom_mens[1]
    fourier_prom_temp_dia_lluv_mens[2] = fourier_tdía_máx_prom_mens[2]

    prom_rad_dia_seco_mens = []
    varia_rad_dia_seco_mens = []
    prom_rad_dia_lluv_mens = []
    varia_rad_dia_lluv_mens = []
    prom_temp_dia_seco_mens = []
    varia_temp_dia_seco_mens = []
    prom_temp_dia_lluv_mens = []
    varia_temp_dia_min_prom = []
    varia_temp_dia_lluv_mens = []
    for m in range(inic, fin+1):
        mes = m % 12 + 1
        prom_rad_dia_seco_mens.append(fourin(fourier_prom_rad_dia_seco_mens, mes))
        prom_rad_dia_lluv_mens.append(fourin(fourier_prom_rad_dia_lluv_mens, mes))
        srdcv = max(fourin(srdcvf, mes), 0.06)
        srwcv = max(fourin(srwcvf, mes), 0.06)
        varia_rad_dia_seco_mens.append(prom_rad_dia_seco_mens * srdcv)
        varia_rad_dia_lluv_mens.append(prom_rad_dia_lluv_mens * srwcv)

        prom_temp_dia_seco_mens.append(fourin(fourier_prom_temp_dia_seco_mens, mes))
        prom_temp_dia_lluv_mens.append(fourin(fourier_prom_temp_dia_lluv_mens, mes))
        varia_temp_dia_seco_mens.append(max(5.8-0.09 * prom_temp_dia_seco_mens[-1], 0.5))
        varia_temp_dia_lluv_mens.append(max(5.8-0.09 * prom_temp_dia_lluv_mens[-1], 0.5))
        varia_temp_dia_min_prom.append(max(5.2-0.13 * tdía_mín_prom_mens[m], 0.5))

    parám['Prom_rad_dia_seco_mens'] = prom_rad_dia_seco_mens
    parám['Varia_rad_dia_seco_mens'] = varia_rad_dia_seco_mens
    parám['Prom_rad_dia_lluv_mens'] = prom_rad_dia_lluv_mens
    parám['Varia_rad_dia_lluv_mens'] = varia_rad_dia_lluv_mens
    parám['Prom_temp_dia_seco_mens'] = prom_temp_dia_seco_mens
    parám['Varia_temp_dia_seco_mens'] = varia_temp_dia_seco_mens
    parám['Prom_temp_dia_lluv_mens'] = prom_temp_dia_lluv_mens
    parám['Varia_temp_dia_lluv_mens'] = varia_temp_dia_lluv_mens
    parám['Varia_temp_dia_min_prom'] = varia_temp_dia_min_prom

    parám['Alpha_distgamma_prec'] = alpha_distgamma_prec
    parám['Prec_total_prom_mens'] = prec_total_prom_mens
    parám['Prob_lluv_después_seco'] = prob_lluv_después_seco
    parám['Prom_días_prec_mens'] = prom_días_prec_mens

    return parám


def generar(parám, lat, fecha_inic, fecha_fin):
    generados = {'Rad_sol': [], 'Temp_máx': [], 'Temp_mín': [], 'Precip': [], 'Rad_foto': []}

    fechas = [fecha_inic + ft.timedelta(days=x) for x in list(range(ft.timedelta(fecha_fin, fecha_inic)))]
    llovió_ayer = False
    x_prev = np.zeros(3)

    correcciones = corregir(parám)

    for n, f in enumerate(fechas):
        parám_día = {}
        for p in parám:
            if p != 'Mes':
                for k, m in enumerate(parám['Mes']):
                    if f < m:
                        continue
                    else:
                        diff = parám[p][k] - parám[p][k-1]
                        estimo = parám[p][k-1] + diff * (f-parám['Mes'][k-1]).days
                        corrección = correcciones[p][k]
                        parám_día[p] = estimo + corrección

        prom_rad_dia_seco_mens = parám_día['Prom_rad_dia_seco_mens']
        varia_rad_dia_seco_mens = parám_día['Varia_rad_dia_seco_mens']
        prom_rad_dia_lluv_mens = parám_día['Prom_rad_dia_lluv_mens']
        varia_rad_dia_lluv_mens = parám_día['Varia_rad_dia_lluv_mens']
        prom_temp_dia_seco_mens = parám_día['Prom_temp_dia_seco_mens']
        varia_temp_dia_seco_mens = parám_día['Varia_temp_dia_seco_mens']
        prom_temp_dia_lluv_mens = parám_día['Prom_temp_dia_lluv_mens']
        varia_temp_dia_lluv_mens = parám_día['Varia_temp_dia_lluv_mens']
        tdía_mín_prom_mens = parám_día['Tdía_mín_prom_mens']
        varia_temp_dia_min_prom = parám_día['Varia_temp_dia_min_prom']
        alpha_distgamma_prec = min(parám_día['Alpha_distgamma_prec'], 0.998)
        beta_distgamma_prec = max(parám_día['Beta_distgamma_prec'], 1.1)
        prob_lluv_después_seco = min(max(parám_día['Prob_lluv_después_seco'], 0), 1)
        prob_lluv_después_lluv = min(max(parám_día['Prob_lluv_después_lluv'], 0), 1)

        rad_máx = rad_entrando(f.day, lat) * 0.8
        rad_mín = 0.2 * rad_máx

        alea = aleatorio.uniform(0, 1)
        if (not llovió_ayer and alea < prob_lluv_después_seco) or (llovió_ayer and alea < prob_lluv_después_lluv):
            aa = 1 / alpha_distgamma_prec
            ab = 1 / (1 - alpha_distgamma_prec)
            tr1 = mat.exp(-18.42/aa)
            tr2 = mat.exp(-18.42/ab)
            s1 = 1
            s2 = 1

            while (s1+s2) > 1:
                alea = aleatorio.uniform(0, 1)
                if alea <= tr1:
                    s1 = 0
                else:
                    s1 = alea**aa
                alea = aleatorio.uniform(0, 1)
                if alea <= tr2:
                    s2 = 0
                else:
                    s2 = alea ** ab

            z = s1 / (s1+s2)
            alea = aleatorio.uniform(0, 1)
            precip = max(-z * mat.log(alea) * beta_distgamma_prec, 0.1)
        else:
            precip = 0

        if precip < 0.0001:
            llovió = False
        else:
            llovió = True

        # Generar temp_máx, temp_mín, y rad_sol
        if llovió:
            prom_rad = prom_rad_dia_lluv_mens
            varia_rad = varia_rad_dia_lluv_mens
            prom_tempmáx = prom_temp_dia_lluv_mens
            varia_tempmáx = varia_temp_dia_lluv_mens
        else:
            prom_rad = prom_rad_dia_seco_mens
            varia_rad = varia_rad_dia_seco_mens
            prom_tempmáx = prom_temp_dia_seco_mens
            varia_tempmáx = varia_temp_dia_seco_mens

        e = np.zeros(3)
        k = 1
        while k <= 2:
            alea_1 = aleatorio.uniform(0, 1)
            alea_2 = aleatorio.uniform(0, 1)
            v = mat.sqrt(-2 * mat.log(alea_1))*mat.cos(2 * mat.pi * alea_2)
            if abs(v) <= 2.5:
                e[k] = v
                k += 1

        b = np.array([[0.781, 0, 0], [0.328, 0.637, 0], [0.238, -0.341, 0.873]])
        a = np.array([[0.567, 0.086, -0.002], [0.253, 0.504, -0.050], [-0.006, -0.039, 0.244]])

        r = b * np.reshape(e, (3, 1))
        rr = a * np.reshape(x_prev, (3, 1))
        x = r + rr

        temp_máx = x[0] * varia_tempmáx + prom_tempmáx
        temp_mín = x[1] * varia_temp_dia_min_prom + tdía_mín_prom_mens
        rad_sol = x[2] * varia_rad + prom_rad
        rad_sol = min(max(rad_sol, rad_mín), rad_máx)

        rad_foto = rad_sol * 2

        if temp_mín > temp_máx:
            temp = temp_máx
            temp_máx = temp_mín
            temp_mín = temp

        if (temp_máx - temp_mín) < 0.1:
            temp_máx += 0.1

        llovió_ayer = llovió

        x_prev = x.copy()
        generados['Rad_sol'].append(rad_sol)
        generados['Temp_máx'].append(temp_máx)
        generados['Temp_mín'].append(temp_mín)
        generados['Precip'].append(precip)
        generados['Rad_foto'].append(rad_foto)
    return generados


def rad_entrando(día, lat):
    radios = mat.pi / 180
    t = 2 * mat.pi * (día + 10)/365
    c1 = mat.cos(t)
    dec = - 23.45 * c1
    ssin = mat.sin(radios*dec) * mat.sin(radios * lat)
    ccos = mat.cos(radios*dec) * mat.cos(radios*lat)
    soc = ssin / ccos
    soc = min(max(soc, -1), 1)
    dayl = 12 + 24 * mat.asin(soc)/mat.pi
    dsinb = 3600 * (dayl*ssin + 24/mat.pi*ccos*mat.sqrt(1-soc**2))
    sc = 1368 * (1 + 0.033*mat.cos(2*mat.pi*día/365))

    s0d = sc * dsinb
    rad = s0d / 1E6
    return rad


def corregir(parám):
    correcciones = {}

    for p in parám:
        correcciones[p] = []
        if p != 'Mes':
            for m in parám['Mes']:
                corrección = parám[p][m] - (0.25 * (parám[p][m-1] + 2 * parám[p][m] + parám[p][m+1]))
                correcciones[p].append(corrección)
    return correcciones


def fourcf(y):
    rad = 2 * mat.pi / 12
    sum0 = 0.0
    sum1 = 0.0
    sum2 = 0.0
    for m in range(len(y)):
        x = rad * ((m+1)-0.5)
        sum0 += y[m]
        sum1 += y[m] * mat.cos(x)
        sum2 += y[m] * mat.sin(x)
    a1 = sum1 / 6
    a2 = sum2 / 6
    t = mat.atan2(a2, a1)
    if t < 0:
        t += 2 * mat.pi
    coef = np.zeros(3)
    coef[0] = sum0 / 12
    coef[1] = a1 / mat.cos(t)
    coef[2] = t

    return coef


def fourin(coef, mes):
    rad = 2 * mat.pi / 12
    x = rad * (mes-0.5)

    return coef[0] + coef[1] * mat.cos(x-coef[2])
