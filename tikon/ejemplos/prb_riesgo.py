import itertools
import os
from copy import deepcopy
from functools import partial
from multiprocessing import Pool as Reserva

import matplotlib.cm as cm
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura
from scipy.signal import savgol_filter
from tikon.ejemplos import en_ejemplos
from tikon.ejemplos.prb import red, Paras_pupa, exper_A, Paras_larvas, Oarenosella
from tikon.central.modelo import Simulador
from tikon.móds.manejo import Manejo, Regla
from tikon.móds.manejo.acciones import AgregarPob, MultPob
from tikon.móds.manejo.conds import CondTiempo, CondPoblación, SuperiorOIgual, CondCada, Inferior
from tikon.utils import guardar_json, leer_json

red.cargar_calibs(en_ejemplos('calibs Sitio A epm ens final/red'))
exper_A.cargar_calibs(en_ejemplos('calibs Sitio A epm ens final'))

borrar = False
umbral = 655757.1429 * 0.5
etapas = [e for o in red for e in o]
fantasmas_larva = ['Parasitoide larvas juvenil en O. arenosella juvenil_{}'.format(i) for i in range(3, 6)]
fantasmas_pupa = ['Parasitoide pupa juvenil en O. arenosella pupa']
# https://www.researchgate.net/publication/328653320_Biological_suppression_of_coconut_black_headed_caterpillar_Opisina_arenosella_outbreak_in_East_Godavari_district_of_Andhra_Pradesh-eco_friendly_technology
dosis_paras = 600000
dosis_paras_dinám = dosis_paras / 3

tiempos = range(1, 61, 2)
mort = 0.05
acciones = {
    'pstcd adultos': [MultPob(e, mort) for e in etapas if e.nombre == 'adulto'],
    'pstcd expt huevos': [MultPob(e, mort) for e in
                          [x for x in etapas if x.nombre != 'huevo'] + fantasmas_larva + fantasmas_pupa],
    'pstcd expt pupas': [MultPob(e, mort) for e in [x for x in etapas if x.nombre != 'pupa'] + fantasmas_larva],
    'pstcd expt sedent': [
        MultPob(e, mort) for e in [x for x in etapas if x.nombre != 'pupa' and x.nombre != 'huevo'] + fantasmas_larva
    ],
    'pstcd general': [MultPob(e, mort) for e in etapas + fantasmas_larva + fantasmas_pupa],
    'pstcd larvas': [MultPob(e, mort) for e in
                     [x for x in etapas if x.org is Oarenosella and 'juvenil' in x.nombre] + fantasmas_larva],
    'pstcd antisel': [MultPob(e, mort) for e in [x for x in Oarenosella] + fantasmas_larva + fantasmas_pupa] +
                     [MultPob(e, mort * 0.1) for o in [Paras_pupa, Paras_larvas] for e in o],
    'biocntrl larva': AgregarPob(Paras_larvas['adulto'], dosis_paras),
    'biocntrl pupa': AgregarPob(Paras_pupa['adulto'], dosis_paras),
    'biocontrol ambos': [AgregarPob(Paras_larvas['adulto'], dosis_paras / 2),
                         AgregarPob(Paras_pupa['adulto'], dosis_paras / 2)],
}
corridas = {
    f'{a} {t}': Manejo(Regla(CondTiempo(t), acciones[a])) for t, a in itertools.product(tiempos, acciones)
}

dinámicas_larvas = {
    # 'dinámica lrv umbr huevo': {'etp umbr': Oarenosella['huevo'], 'acc': Paras_larvas['adulto']},
    'dinámica lrv umbr larva': {
        'etp umbr': [e for e in Oarenosella if e.nombre.startswith('juvenil')],
        'acc': AgregarPob(Paras_larvas['adulto'], dosis_paras_dinám)
    },
    'dinámica pupa umbr larva': {
        'etp umbr': [e for e in Oarenosella if e.nombre.startswith('juvenil')],
        'acc': AgregarPob(Paras_pupa['adulto'], dosis_paras_dinám)
    },
    'dinámica pstcd excpt huevos umbr larva': {
        'etp umbr': [e for e in Oarenosella if e.nombre.startswith('juvenil')],
        'acc': [MultPob(x, mort) for x in
                ([e for e in etapas if e.nombre != 'huevo'] + fantasmas_larva + fantasmas_pupa)]
    }
}
dinámicas_pupas = {
    'dinámica lrv umbr adulto': {'etp umbr': Oarenosella['adulto'], 'acc': Paras_larvas['adulto']},
    'dinámica lrv umbr pupa': {'etp umbr': Oarenosella['pupa'], 'acc': Paras_larvas['adulto']},
    # 'dinámica pupa umbr huevo': {'etp umbr': Oarenosella['huevo'], 'acc': Paras_pupa['adulto']},
    'dinámica pupa umbr adulto': {'etp umbr': Oarenosella['adulto'], 'acc': Paras_pupa['adulto']},
    'dinámica pupa umbr pupa': {'etp umbr': Oarenosella['pupa'], 'acc': Paras_pupa['adulto']}
}
umb_máx_larvas = umbral
n = 20
umbrales_larvas = range(int(umb_máx_larvas // n), int(umb_máx_larvas + umb_máx_larvas // n), int(umb_máx_larvas // n))

corridas_dinámicas_larvas = {
    f'{d} {u}': Manejo(Regla(
        CondPoblación(dinámicas_larvas[d]['etp umbr'], SuperiorOIgual(u), espera=30),
        dinámicas_larvas[d]['acc']
    )) for u, d in itertools.product(umbrales_larvas, dinámicas_larvas)
}

umb_máx_pupas = umbral
n = 20
umbrales_pupas = range(int(umb_máx_larvas // n), int(umb_máx_larvas + umb_máx_larvas // n), int(umb_máx_larvas // n))

corridas_dinámicas_pupas = {
    f'{d} {u}': Manejo(Regla(
        CondPoblación(dinámicas_pupas[d]['etp umbr'], SuperiorOIgual(u), espera=30),
        AgregarPob(dinámicas_pupas[d]['acc'], dosis_paras_dinám)
    )) for u, d in itertools.product(umbrales_pupas, dinámicas_pupas)
}

corridas['sin control'] = Manejo()
corridas['sin paras pupa'] = Manejo(Regla(CondCada(1), MultPob('Parasitoide pupa adulto', 0)))
corridas['sin paras larvas'] = Manejo(Regla(CondCada(1), MultPob('Parasitoide larvas adulto', 0)))
corridas['sin paras larvas < 150'] = Manejo(
    [Regla(CondTiempo(150, Inferior), MultPob('Parasitoide larvas adulto', 0)),
     Regla(CondTiempo(150), AgregarPob('Parasitoide larvas adulto', 100000))]
)
corridas['sin paras pupa < 150'] = Manejo(
    [Regla(CondTiempo(150, Inferior), MultPob('Parasitoide pupa adulto', 0)),
     # Regla(CondTiempo(150), AgregarPob('Parasitoide pupa adulto', 100000))
     ]
)
corridas['sin paras intercambio a 150'] = Manejo(
    [Regla(CondTiempo(150, Inferior), MultPob('Parasitoide pupa adulto', 0)),
     Regla(CondTiempo(150, SuperiorOIgual), MultPob('Parasitoide larvas adulto', 0))
     ]
)
corridas['pstcd expt huevos cada 30'] = Manejo(
    Regla(CondCada(30),
          [MultPob(x, mort) for x in ([e for e in etapas if e.nombre != 'huevo'] + fantasmas_larva + fantasmas_pupa)]),

)
corridas['pstcd expt huevos cada 60'] = Manejo(
    Regla(CondCada(60),
          [MultPob(x, mort) for x in ([e for e in etapas if e.nombre != 'huevo'] + fantasmas_larva + fantasmas_pupa)]),

)

dir_res = 'anlz riesgo'


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


def _procesar_res(res, todos=False):
    d_res = {}
    for v in res['red']:
        if v.matr_t is not None:
            d_res[str(v)] = {}
            for e in v.matr_t.dims._coords['etapa']:
                d_res[str(v)][str(e)] = v.matr_t.obt_valor(índs={'etapa': e}).tolist()

    d_res_final = {
        'suma_larvas': np.sum([d_res['Pobs']['O. arenosella juvenil_%i' % i] for i in range(1, 6)], axis=0)
    }
    if todos:
        d_res_final.update(d_res['Pobs'])
    return d_res_final


def correr(*args):
    nombre, mnj = args[0]
    copia_red = deepcopy(red)
    exp = deepcopy(exper_A)

    dir_egr = f'{dir_res}/{nombre}'

    print(f'Corriendo {nombre}')
    simul = Simulador([copia_red, mnj])
    res = simul.simular(400, n_rep_parám=50, n_rep_estoc=5, exper=exp)

    d_res_final = _procesar_res(res, todos=nombre == 'sin control')

    guardar_json(d_res_final, archivo=dir_egr + '/res.json')
    res.graficar(dir_egr)


def _correr_con_biocntrl(días_cntrl, dev_eval=True, pupa=0):
    copia_red = deepcopy(red)
    exp = deepcopy(exper_A)
    n_días = len(días_cntrl)
    dosis = dosis_paras / n_días
    acción = [AgregarPob(Paras_pupa['adulto'] if (t < pupa) else Paras_larvas['adulto'], dosis) for t in range(n_días)]
    mnj = Manejo([Regla(CondTiempo(int(t)), a) for a, t in zip(acción, días_cntrl)])

    print('Corriendo biocontrol opt días: ' + ', '.join(str(round(x)) for x in días_cntrl))
    print(días_cntrl)
    simul = Simulador([copia_red, mnj])
    res = simul.simular(400, n_rep_parám=50, n_rep_estoc=5, exper=exp)

    d_res_final = _procesar_res(res)

    eval_ = np.sum(np.maximum(0, d_res_final['suma_larvas'] - umbral)) / umbral
    print(eval_)
    return eval_ if dev_eval else res


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

    acciones_interés = ['pstcd expt huevos', 'pstcd general', 'biocntrl pupa']  # , 'biocntrl larva']
    # acciones_interés = ['pstcd expt sedent', 'biocntrl pupa', 'biocntrl larva']
    suma_larvas_base = obt_base()['suma_larvas']

    d_suma_larvas = {}
    for nombre in acciones:
        d_suma_larvas[nombre] = np.array(
            [d['suma_larvas'] for d in [leer_json(f'{dir_res}/{nombre} {t}/res.json') for t in tiempos]])
    suma_larvas_base = obt_base()['suma_larvas']

    def _gen_fig(rebana):
        fig = Figura()
        TelaFigura(fig)
        ejes1 = fig.add_subplot(111)
        for a in acciones_interés:
            cumul_sup = np.array([np.sum(np.maximum(0, t[rebana] - umbral), axis=0) / umbral for t in d_suma_larvas[a]])
            ejes1.plot(tiempos, _alisar(np.median(cumul_sup, axis=(1, 2, 3)), líms=(0, None)), label=a)
            ejes1.fill_between(
                tiempos,
                _alisar(np.percentile(cumul_sup, 5, axis=(1, 2, 3)), líms=(0, None)),
                _alisar(np.percentile(cumul_sup, 95, axis=(1, 2, 3)), líms=(0, None)),
                alpha=0.25
            )
            # ejes1.plot(tiempos, [np.mean(np.greater_equal(t[rebana], umbral)) for t in d_suma_larvas[a]], label=a)
        ejes1.plot(tiempos, np.full(len(tiempos), np.sum(
            np.mean((np.maximum(0, suma_larvas_base[rebana] - umbral)), axis=(1, 2, 3)) / umbral)))

        eje2 = ejes1.twinx()
        eje2.plot(tiempos, np.median(suma_larvas_base[tiempos], axis=(-1, -2)), color='#000000', label='Población')

        ejes1.legend()
        eje2.legend()
        return fig

    _gen_fig(rebana=slice(60, None)).savefig(f'{dir_todo}/sobre_umbral_por_día_acción > 60')
    _gen_fig(rebana=slice(None, 60)).savefig(f'{dir_todo}/sobre_umbral_por_día_acción < 60')

    acciones_interés = ['pstcd expt huevos', 'pstcd general', 'biocntrl pupa']
    fig = Figura()
    TelaFigura(fig)
    ejes1 = fig.add_subplot(111)

    emp = 60

    x = np.arange(emp, suma_larvas_base.shape[0])
    ejes1.plot(x, np.mean(np.greater_equal(suma_larvas_base, umbral), axis=(-1, -2))[emp:], color='#000000',
               label='Sin control')
    fig.savefig(f'{dir_todo}/ACFAS 1 obs')
    for a in acciones_interés:
        prob_sup = np.mean(np.greater_equal(d_suma_larvas[a], umbral), axis=(-1, -2))

        ejes1.plot(x, np.median(prob_sup, axis=0)[emp:], label=a)

        ejes1.fill_between(
            x,
            np.percentile(prob_sup[..., emp:, 0], 5, axis=0),
            np.percentile(prob_sup[..., emp:, 0], 95, axis=0),
            alpha=0.25
        )

    fig.legend()
    fig.savefig(f'{dir_todo}/p_sobre_umbral')

    fig = Figura()
    TelaFigura(fig)
    ejes1 = fig.add_subplot(111)
    mediano_base = np.median(suma_larvas_base, axis=(-1, -2))
    for a in acciones_interés:
        dens_mejor_med_base = np.array(
            [np.mean(t <= mediano_base[..., np.newaxis, np.newaxis], axis=(-1, -2)) for t in d_suma_larvas[a]]
        )

        p_día_mejor_que_nada = np.mean(dens_mejor_med_base, axis=0)[..., 0]

        ejes1.plot(_alisar(p_día_mejor_que_nada, líms=(0, 1)), label=a)

    fig.legend()
    fig.savefig(f'{dir_todo}/p_día_mejor_que_nada.jpg')

    fig = Figura()
    TelaFigura(fig)
    ejes1 = fig.add_subplot(111)
    acciones_interés = {
        'dinámica lrv umbr larva': umbrales_larvas,
        'dinámica pupa umbr pupa': umbrales_pupas
    }  # 'dinámica huevo', 'dinámica pupa'
    d_suma_larvas_din = {}
    for nombre, umbr in acciones_interés.items():
        d_suma_larvas_din[nombre] = np.array(
            [d['suma_larvas'] for d in [leer_json(f'{dir_res}/{nombre} {u}/res.json') for u in umbr]]
        )
    for a, u in acciones_interés.items():
        x = list(u)

        # sum_cumul = np.sum(np.maximum(0, (d_suma_larvas_din[a] - umbral) / umbral)[:, reb], axis=1)[:, 0, ...]
        y = np.mean((d_suma_larvas_din[a] >= umbral), axis=1)[:, 0, ...]
        ejes1.plot(x, np.mean(y, axis=(-2, -1)), label=a)
        ejes1.fill_between(
            x,
            _alisar(np.percentile(y, 2.5, axis=(-2, -1))),
            _alisar(np.percentile(y, 97.5, axis=(-2, -1))),
            alpha=0.25
        )

    ejes1.legend()
    # import matplotlib
    # ejes1.get_xaxis().set_major_formatter(
    #     matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    fig.savefig(f'{dir_todo}/umbral vs. sup umbral cumul.jpg')


def opt_bio(*args):
    nombre, (n, pupa) = args[0]
    dir_res_bio = f'{dir_res}/opt bio m25/{nombre}'
    if not os.path.isdir(dir_res_bio):
        os.makedirs(dir_res_bio)
    arch = f'{dir_res_bio}/mejores días.json'
    if not os.path.isfile(arch):
        print('Calibrando opt bio ' + nombre)
        import spotpy

        class mod_opt(object):
            def __init__(símismo):
                símismo.params = [spotpy.parameter.Uniform(str(i), low=25, high=150, as_int=True) for i in range(n)]

            def parameters(símismo):
                return spotpy.parameter.generate(símismo.params)

            def simulation(símismo, x):
                return _correr_con_biocntrl(np.array(x), pupa=pupa)

            def evaluation(símismo):
                observations = [0]
                return observations

            def objectivefunction(símismo, simulation, evaluation):
                return -np.log(simulation + 1)

        mstrd = spotpy.algorithms.dds(
            mod_opt(), dbformat='ram', parallel='mpc', save_sim=False, alt_objfun=None
        )
        n_días = 300
        mstrd.sample(n_días)
        egr_spotpy = spotpy.analyser.get_parameters(
            mstrd.getdata()[np.argpartition(mstrd.getdata()['like1'], -10)[-10:]]
        )

        egr_spotpy = pd.DataFrame(np.array([list(x) for x in egr_spotpy]))
        egr_spotpy.to_json(arch)
        fig = Figura()
        TelaFigura(fig)
        ejes = fig.add_subplot(111)
        ejes.hist(egr_spotpy.values.flatten())
        fig.savefig(f'{dir_res_bio}/mejores días')
        print(egr_spotpy)
    else:
        egr_spotpy = pd.read_json(arch)

    arch_res = f'{dir_res_bio}/res.json'
    if not os.path.isfile(arch_res):
        mejores_días = egr_spotpy.values
        d_res = {}
        for i, días in enumerate(mejores_días):
            res = _correr_con_biocntrl(días, dev_eval=False, pupa=pupa)
            res.graficar(f'{dir_res_bio}/{i}')
            d_res[str(i)] = _procesar_res(res)
        guardar_json(d_res, arch_res)
    else:
        d_res = leer_json(arch_res)
    if pupa:
        acciones_interés_t = ['biocntrl pupa']
        acciones_interés_u = ['dinámica pupa umbr pupa']
        umbrales = umbrales_pupas
    else:
        acciones_interés_t = ['biocntrl larva']
        acciones_interés_u = ['dinámica lrv umbr larva']
        umbrales = umbrales_larvas
    d_suma_larvas = {}
    for nombre in acciones_interés_t:
        d_suma_larvas[nombre] = np.array(
            [d['suma_larvas'] for d in [leer_json(f'{dir_res}/{nombre} {t}/res.json') for t in tiempos]])
    for nombre in acciones_interés_u:
        d_suma_larvas[nombre] = np.array(
            [d['suma_larvas'] for d in [leer_json(f'{dir_res}/{nombre} {u}/res.json') for u in umbrales]])
    d_suma_larvas['optimizada'] = np.array(
        [d['suma_larvas'] for d in d_res.values()]
    )

    fig = Figura()
    TelaFigura(fig)
    ejes1 = fig.add_subplot(111)
    emp = 50
    for a, v in d_suma_larvas.items():
        prob_sup = np.mean(np.greater_equal(v, umbral), axis=(-1, -2))
        x = np.arange(emp, prob_sup.shape[1])
        ejes1.plot(x, np.mean(prob_sup, axis=0)[emp:], label=a)

        ejes1.fill_between(
            x,
            np.percentile(prob_sup[..., emp:, 0], 5, axis=0),
            np.percentile(prob_sup[..., emp:, 0], 95, axis=0),
            alpha=0.25
        )

    ejes1.legend()
    ejes1.set_ylim((0, 1))
    fig.savefig(f'{dir_res_bio}/p sobre umbral')

    fig = Figura()
    TelaFigura(fig)
    ejes1 = fig.add_subplot(111)
    for a, v in d_suma_larvas.items():
        daño = np.mean(np.maximum(v - umbral, 0) / umbral, axis=(-1, -2))
        x = np.arange(daño.shape[1])
        ejes1.plot(x, np.mean(daño, axis=0)[:, 0], label=a)

        ejes1.fill_between(
            x,
            np.percentile(daño[..., 0], 5, axis=0),
            np.percentile(daño[..., 0], 95, axis=0),
            alpha=0.25
        )

    ejes1.legend()
    fig.savefig(f'{dir_res_bio}/daño')


with Reserva() as r:
    para_correr = {
        ll: v for ll, v in corridas_dinámicas_larvas.items() if
        borrar or not os.path.isfile(dir_res + '/' + ll + '/res.json')
    }
    r.map(correr, para_correr.items())

with Reserva() as r:
    para_correr = {
        ll: v for ll, v in corridas_dinámicas_pupas.items() if
        borrar or not os.path.isfile(dir_res + '/' + ll + '/res.json')
    }
    r.map(correr, para_correr.items())

with Reserva() as r:
    # noinspection PyTypeChecker
    r.map(partial(evaluar, umbrales_larvas), dinámicas_larvas)

with Reserva() as r:
    # noinspection PyTypeChecker
    r.map(partial(evaluar, umbrales_pupas), dinámicas_pupas)

with Reserva() as r:
    para_correr = {
        ll: v for ll, v in corridas.items() if borrar or not os.path.isfile(dir_res + '/' + ll + '/res.json')
    }
    res_grupo = r.map(correr, para_correr.items())

with Reserva() as r:
    # noinspection PyTypeChecker
    r.map(partial(evaluar, tiempos), acciones)

_evaluar_todo()

#
with Reserva(processes=6) as r:
    para_correr = {
        ll: v for ll, v in {
            'pupa 0 de 3': (3, 0),
            'pupa 1 de 3': (3, 1),
            'pupa 2 de 3': (3, 2),
            'pupa 3 de 3': (3, 3),
            # 'pupa 0 de 4': (4, 0),
            # 'pupa 1 de 4': (4, 1),
            # 'pupa 2 de 4': (4, 2),
            # 'pupa 3 de 4': (4, 3),
            # 'pupa 4 de 4': (4, 4),
            # 'pupa 0 de 2': (2, 0),
            # 'pupa 1 de 2': (2, 1),
            # 'pupa 2 de 2': (2, 2),
        }.items() if borrar or not os.path.isfile(dir_res + '/' + ll + '/res.json')
    }
    r.map(opt_bio, para_correr.items())
