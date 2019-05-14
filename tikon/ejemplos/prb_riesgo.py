import itertools
import os
from copy import deepcopy
from functools import partial
from multiprocessing import Pool as Reserva

import matplotlib.cm as cm
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura
from scipy.signal import savgol_filter

from tikon.ejemplos import en_ejemplos
from tikon.ejemplos.prb import red, Paras_pupa, exper_A, Paras_larvas, Oarenosella
from tikon.estruc.simulador import Simulador
from tikon.manejo.acciones import AgregarPob, MultPob
from tikon.manejo.conds import CondTiempo, CondPoblación, SuperiorOIgual
from tikon.manejo.manejo import Manejo, Regla
from tikon.utils import guardar_json, leer_json

red.cargar_calib(en_ejemplos('calibs Sitio A epm ens final/red'))
exper_A.cargar_calib(en_ejemplos('calibs Sitio A epm ens final'))

borrar = False

etapas = [e for o in red for e in o]
fantasmas_larva = ['Parasitoide larvas juvenil en O. arenosella juvenil_{}'.format(i) for i in range(2, 6)]
fantasmas_pupa = ['Parasitoide pupa juvenil en O. arenosella pupa']
# https://www.researchgate.net/publication/328653320_Biological_suppression_of_coconut_black_headed_caterpillar_Opisina_arenosella_outbreak_in_East_Godavari_district_of_Andhra_Pradesh-eco_friendly_technology
dosis_paras = 600000
dosis_paras_dinám = dosis_paras

tiempos = range(1, 61, 2)
acciones = {
    'pstcd adultos': [MultPob(e, 0.05) for e in etapas if e.nombre == 'adulto'],
    'pstcd expt huevos': [MultPob(e, 0.05) for e in
                          [x for x in etapas if x.nombre != 'huevo'] + fantasmas_larva + fantasmas_pupa],
    'pstcd expt pupas': [MultPob(e, 0.05) for e in [x for x in etapas if x.nombre != 'pupa'] + fantasmas_larva],
    'pstcd expt sedent': [
        MultPob(e, 0.05) for e in [x for x in etapas if x.nombre != 'pupa' and x.nombre != 'huevo'] + fantasmas_larva
    ],
    'pstcd general': [MultPob(e, 0.05) for e in etapas + fantasmas_larva + fantasmas_pupa],
    'pstcd larvas': [MultPob(e, 0.05) for e in
                     [x for x in etapas if x.org is Oarenosella and 'juvenil' in x.nombre] + fantasmas_larva],
    'pstcd antisel': [MultPob(e, 0.05) for e in [x for x in Oarenosella] + fantasmas_larva + fantasmas_pupa] +
                     [MultPob(e, 0.01) for o in [Paras_pupa, Paras_larvas] for e in o],
    'biocntrl larva': AgregarPob(Paras_larvas['adulto'], dosis_paras),
    'biocntrl pupa': AgregarPob(Paras_pupa['adulto'], dosis_paras),
    'biocontrol ambos': [AgregarPob(Paras_larvas['adulto'], dosis_paras), AgregarPob(Paras_pupa['adulto'], dosis_paras)]
}
corridas = {
    f'{a} {t}': Manejo(Regla(CondTiempo(t), acciones[a])) for t, a in itertools.product(tiempos, acciones)
}

dinámicas = {
    'dinámica huevo': Oarenosella['huevo'],
    'dinámica larva': [e for e in Oarenosella if e.nombre.startswith('juvenil')],
    'dinámica adulto': Oarenosella['adulto'],
    'dinámica pupa': Oarenosella['pupa'],
}
umbrales = range(400000 // 20, 400000 + 400000 // 20, 400000 // 20)

corridas_dinámicas = {
    f'{d} {u}': Manejo(Regla(
        CondPoblación(dinámicas[d], SuperiorOIgual(u), espera=30), AgregarPob(Paras_larvas['adulto'], dosis_paras_dinám)
    )) for u, d in itertools.product(umbrales, dinámicas)
}

corridas['sin control'] = Manejo()

dir_res = 'anlz riesgo'
umbral = 655757.1429 * 0.5


def obt_base():
    arch_base = f'{dir_res}/sin control/res.json'
    try:
        d_res_base = leer_json(arch_base)
    except FileNotFoundError:
        exp = deepcopy(exper_A)
        copia_red = deepcopy(red)
        d_res_base = Simulador(copia_red).simular(600, n_rep_parám=50, n_rep_estoc=5, exper=exp)
        d_res_final = {
            'suma_larvas': np.sum([
                [d_res_base['Pobs']['O. arenosella juvenil_%i' % i] for i in range(1, 6)]
            ], axis=0)
        }
        guardar_json(d_res_final, archivo=arch_base)

    return d_res_base


def correr(*args):
    nombre, mnj = args[0]
    copia_red = deepcopy(red)
    exp = deepcopy(exper_A)

    dir_egr = f'{dir_res}/{nombre}'

    print(f'Corriendo {nombre}')
    simul = Simulador([copia_red, mnj])
    res = simul.simular(400, n_rep_parám=50, n_rep_estoc=5, exper=exp)
    d_res = {}
    for v in res['red']:
        if v.matr_t is not None:
            d_res[str(v)] = {}
            for e in v.matr_t.dims._coords['etapa']:
                d_res[str(v)][str(e)] = v.matr_t.obt_valor(índs={'etapa': e}).tolist()

    d_res_final = {
        'suma_larvas': np.sum([d_res['Pobs']['O. arenosella juvenil_%i' % i] for i in range(1, 6)], axis=0)
    }

    guardar_json(d_res_final, archivo=dir_egr + '/res.json')
    res.graficar(dir_egr)


def _alisar(m, ventana=15, polí=3, líms=None):
    m = savgol_filter(m, ventana, polí)
    if líms is not None:
        if líms[0] is not None:
            m = np.maximum(m, líms[0])
        if líms[1] is not None:
            m = np.minimum(m, líms[1])
    return m


def evaluar(*args):
    n, nombre = args
    print(f'Procesando {nombre}')

    if not os.path.isdir(f'{dir_res}/{nombre}'):
        os.makedirs(f'{dir_res}/{nombre}')

    suma_larvas = np.array([d['suma_larvas'] for d in [leer_json(f'{dir_res}/{nombre} {t}/res.json') for t in n]])
    suma_larvas_base = obt_base()['suma_larvas']

    prob_sup_umbral = np.mean(suma_larvas > umbral, axis=(-1, -2))
    prob_base_sup_umbral = np.mean(suma_larvas_base > umbral, axis=(-1, -2))

    ratio = prob_sup_umbral / prob_base_sup_umbral
    ratio[np.isnan(ratio)] = 1

    def _dibujar(líns, arch):
        fig = Figura()
        TelaFigura(fig)
        ejes = fig.add_subplot(111)
        colores = cm.jet(np.linspace(0, 1, len(líns)))
        for i, l in enumerate(líns):
            ejes.plot(l, color=colores[i], label=str(i))
        ejes.legend()
        fig.savefig(arch)

    def _hist(pnts, arch, ref=None):
        fig = Figura()
        TelaFigura(fig)
        ejes = fig.add_subplot(111)
        ejes.hist(pnts)
        if ref is not None:
            ejes.axvline(ref, color='k', linestyle='dashed', linewidth=1)
        fig.savefig(arch)

    def _combinar(m, cntrl):
        return np.concatenate((m, cntrl.reshape((1, *cntrl.shape))), axis=0)

    _hist(
        [np.log(np.sum(np.maximum(0, t - umbral)) / umbral + 1) for t in suma_larvas],
        f'{dir_res}/{nombre}/cumul sobre umbral.jpg',
        ref=np.log(np.sum(np.maximum(0, suma_larvas_base - umbral)) / umbral + 1)
    )
    _dibujar(
        [[np.sum(np.maximum(0, t - umbral)) / umbral for t in suma_larvas]],
        f'{dir_res}/{nombre}/sobre_umbral_por_día_acción'
    )

    p_día_90 = np.mean(prob_sup_umbral <= 0.10, axis=0)

    mediano_base = np.median(suma_larvas_base, axis=(-1, -2))
    dens_mejor_med_base = np.array(
        [np.mean(t <= mediano_base[..., np.newaxis, np.newaxis], axis=(-1, -2)) for t in suma_larvas]
    )

    _dibujar(dens_mejor_med_base, f'{dir_res}/{nombre}/dens mejor med base.jpg')

    p_día_mejor_o_nada = np.mean(dens_mejor_med_base >= 0.5, axis=0)
    _dibujar([_alisar(p_día_mejor_o_nada[..., 0], líms=(0, 1))], f'{dir_res}/{nombre}/p_día_mejor_que_nada.jpg')
    _dibujar([_alisar(p_día_90[..., 0], líms=(0, 1))], f'{dir_res}/{nombre}/p_día_90%_bajo_umbral.jpg')
    _dibujar(_combinar(prob_sup_umbral, prob_base_sup_umbral), f'{dir_res}/{nombre}/p_sup_umbral.jpg')

    if n == tiempos:

        def _ajust_t(m):

            m_rel = m.copy()
            for i, t in enumerate(n):
                m_rel[i, :m.shape[1] - t, ...] = m[i, t:, ...]
                m_rel[i, m.shape[1] - t:, ...] = np.nan
            return m_rel

        _dibujar(
            _ajust_t(_combinar(prob_sup_umbral, prob_base_sup_umbral)), f'{dir_res}/{nombre}/p_sup_umbral_rel_apli.jpg'
        )
        _dibujar(_ajust_t(dens_mejor_med_base), f'{dir_res}/{nombre}/dens mejor med base rel apli.jpg')

    _dibujar([_alisar(t[..., 0]) for t in ratio], f'{dir_res}/{nombre}/ratio.jpg')


def _evaluar_todo():
    dir_todo = f'{dir_res}/eval'
    if not os.path.isdir(dir_todo):
        os.makedirs(dir_todo)

    acciones_interés = ['pstcd expt sedent', 'biocntrl pupa', 'biocntrl larva']

    d_suma_larvas = {}
    for nombre in acciones_interés:
        d_suma_larvas[nombre] = np.array(
            [d['suma_larvas'] for d in [leer_json(f'{dir_res}/{nombre} {t}/res.json') for t in tiempos]])
    suma_larvas_base = obt_base()['suma_larvas']

    fig = Figura()
    TelaFigura(fig)
    ejes1 = fig.add_subplot(111)
    for i, n in enumerate(d_suma_larvas):
        # ejes1.plot(tiempos, [np.sum(np.maximum(0, t - umbral)) / umbral for t in d_suma_larvas[n]], label=n)
        ejes1.plot(tiempos, _alisar([np.mean(np.greater_equal(t, umbral)) for t in d_suma_larvas[n]]), label=n)

    eje2 = ejes1.twinx()
    eje2.plot(tiempos, np.mean(suma_larvas_base[tiempos], axis=(-1, -2)), color='#000000', label='Población')

    ejes1.legend()
    eje2.legend()
    fig.savefig(f'{dir_todo}/p_sobre_umbral_por_día_acción')
    eje2.clear()


with Reserva() as r:
    para_correr = {
        ll: v for ll, v in corridas_dinámicas.items() if borrar or not os.path.isfile(dir_res + '/' + ll + '/res.json')
    }
    res_dinámico = r.map(correr, para_correr.items())

with Reserva() as r:
    # noinspection PyTypeChecker
    r.map(partial(evaluar, umbrales), dinámicas)

with Reserva() as r:
    para_correr = {
        ll: v for ll, v in corridas.items() if borrar or not os.path.isfile(dir_res + '/' + ll + '/res.json')
    }
    res_grupo = r.map(correr, para_correr.items())

with Reserva() as r:
    # noinspection PyTypeChecker
    r.map(partial(evaluar, tiempos), acciones)


_evaluar_todo()
