import os
from multiprocessing import Pool as Reserva

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura
from tikon.ejemplos import en_ejemplos
from tikon.ejemplos.prb import red, Paras_pupa, exper_A, Paras_larvas
from tikon.estruc.modelo import Simulador
from tikon.móds.manejo import Manejo, Regla
from tikon.móds.manejo.acciones import AgregarPob, MultPob
from tikon.móds.manejo.conds import CondTiempo
from tikon.utils import leer_json, guardar_json

red.cargar_calibs(en_ejemplos('calibs Sitio A epm ens final/red'))
exper_A.cargar_calibs(en_ejemplos('calibs Sitio A epm ens final'))

t = 50
días = 300
dósis = 1000000
umbral = 655757.1429 * 0.5


def correr(*args):
    nombre, simulador = args[0]
    dir_ = 'prb3/imgs'
    arch = f'{dir_}/{nombre}.json'
    if os.path.isfile(arch):
        return {ll: np.array(v) for ll, v in leer_json(arch).items()}
    print(f'Corriendo {nombre}')
    res = simulador.simular(días=días, exper=exper_A)
    res.graficar(f'prb3/{nombre}')

    res_corrida = _extraer_pobs(res)
    pobs_larvas = sumar_larvas(res_corrida)
    suma = np.mean(np.sum(
        np.maximum(pobs_larvas - umbral, 0),
        axis=0), axis=(-1, -2)
    )
    print(f'{nombre}: {suma / umbral}')
    guardar_json({ll: v.tolist() for ll, v in res_corrida.items()}, archivo=arch)

    return res_corrida


def sumar_larvas(res_corrida):
    return np.sum([res_corrida['O. arenosella juvenil_%i' % i] for i in range(1, 6)], axis=0)


def _extraer_pobs(res):
    d_res = {}
    for e in res['red']['Pobs'].matr_t.dims._coords['etapa']:
        d_res[str(e)] = res['red']['Pobs'].matr_t.obt_valor(índs={'etapa': e})
    return d_res


def obt_obs(etapa):
    return exper_A.obs['red']['Pobs'].obt_valor({'etapa': etapa})[:, 0]


manejo_pesticida_excepto_pupa = Manejo(
    Regla(CondTiempo(t), [MultPob(e, 0.05) for o in red for e in o if e.nombre != 'pupa'])
)
manejo_pesticida_adultos = Manejo(
    Regla(CondTiempo(t), [MultPob(e, 0.05) for o in red for e in o if e.nombre == 'adulto'])
)
manejo_pesticida_excepto_huevos = Manejo(
    Regla(CondTiempo(t), [MultPob(e, 0.05) for o in red for e in o if e.nombre != 'huevo'])
)

manejo_pesticida_todo = Manejo(
    Regla(CondTiempo(t), [MultPob(e, 0.05) for o in red for e in o])
)

manejo_larva = Manejo(Regla(CondTiempo(t), AgregarPob(Paras_larvas['adulto'], dósis)))

manejo_larva_multi = Manejo([
    Regla(CondTiempo(t - 7), AgregarPob(Paras_larvas['adulto'], dósis / 3)),
    Regla(CondTiempo(t), AgregarPob(Paras_larvas['adulto'], dósis / 3)),
    Regla(CondTiempo(t + 7), AgregarPob(Paras_larvas['adulto'], dósis / 3))
])

manejo_pupa = Manejo(Regla(CondTiempo(t), AgregarPob(Paras_pupa['adulto'], dósis)))

manejo_ambos = Manejo([
    Regla(CondTiempo(t), AgregarPob(Paras_larvas['adulto'], dósis / 2)),
    Regla(CondTiempo(t), AgregarPob(Paras_pupa['adulto'], dósis / 2))
])

corridas = {
    # 'con pesticida sin pupas 95%': Simulador([red, manejo_pesticida_excepto_pupa]),
    # 'con pesticida adultos 95%': Simulador([red, manejo_pesticida_adultos]),
    # 'con pesticida sin huevos 95%': Simulador([red, manejo_pesticida_excepto_huevos]),
    # 'con pesticida 95%': Simulador([red, manejo_pesticida_todo]),
    'con biocontrol larva': Simulador([red, manejo_larva]),
    'con biocontrol larva multi': Simulador([red, manejo_larva_multi]),
    'con biocontrol pupa': Simulador([red, manejo_pupa]),
    'con biocontrol ambos': Simulador([red, manejo_ambos]),
    'sin biocontrol': Simulador(red)
}

with Reserva() as r:
    res_todo = r.map(correr, corridas.items())


def _graficar_pobs(ej, m_res):
    color = '#99CC00'
    e_t, e_parc, e_estoc, e_parám = (0, 1, -1, -2)

    x = np.arange(m_res.shape[e_t])

    ej.plot(x, m_res.mean(axis=(e_estoc, e_parc, e_parám)), lw=2, color=color, label='Promedio')

    percentiles = [50, 75, 95]
    percentiles.sort()

    # Mínimo y máximo del percentil anterior
    máx_perc_ant = mín_perc_ant = np.median(m_res, axis=(e_estoc, e_parc, e_parám))

    # Para cada percentil...
    for n, p in enumerate(percentiles):
        # Percentiles máximos y mínimos
        máx_perc = np.percentile(m_res, 50 + p / 2, axis=(e_estoc, e_parc, e_parám))
        mín_perc = np.percentile(m_res, (100 - p) / 2, axis=(e_estoc, e_parc, e_parám))

        # Calcular el % de opacidad y dibujar
        op_máx = 0.6
        op_mín = 0.2
        opacidad = (1 - n / (len(percentiles) - 1)) * (op_máx - op_mín) + op_mín

        ej.fill_between(
            x, máx_perc_ant, máx_perc,
            facecolor=color, alpha=opacidad, linewidth=0.5, edgecolor=color, label='IC {} %'.format(p)
        )
        ej.fill_between(
            x, mín_perc, mín_perc_ant,
            facecolor=color, alpha=opacidad, linewidth=0.5, edgecolor=color
        )

        # Guardar los máximos y mínimos
        mín_perc_ant = mín_perc
        máx_perc_ant = máx_perc

    ej.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

    ej.tick_params(axis="x", labelsize=15)
    ej.tick_params(axis="y", labelsize=15)


def _graficar_obs(ej, etapa):
    obs = obt_obs(etapa)
    tiempo = exper_A.obs['red']['Pobs'].eje_tiempo.días
    ej.plot(tiempo, obs, color='#000000', marker='o', markersize=3, label='Observados')


fig = Figura(figsize=(6 * 3, 6.5))
TelaFigura(fig)
ejes = [eje, eje2, eje3] = fig.subplots(ncols=3, sharey='all')
_graficar_pobs(eje, sumar_larvas(res_todo[4]))
_graficar_pobs(eje2, sumar_larvas(res_todo[0]))
_graficar_pobs(eje3, sumar_larvas(res_todo[1]))
for e in ejes:
    líms = e.get_xlim()
    e.plot(np.arange(días), np.full(días, umbral), linestyle='--', color='#000000', label='UDE')
eje2.set_xlabel('Días', fontsize=20)
eje.set_ylabel('Población (ha-1)', fontsize=20)

fig.legend(
    *eje.get_legend_handles_labels(), loc='lower center', ncol=6, fontsize=20,
    # bbox_to_anchor=(0.5, 0.05)
)
fig.subplots_adjust(bottom=0.25)
fig.savefig('Artículo 1 Fig 6.png')

fig = Figura(figsize=(12, 10))
TelaFigura(fig)
(eje, eje2), (eje3, eje4) = fig.subplots(ncols=2, nrows=2, sharex='col')
_graficar_pobs(eje, res_todo[4]['O. arenosella juvenil_5'])
_graficar_pobs(eje2, res_todo[4]['O. arenosella pupa'])
_graficar_pobs(eje3, res_todo[4]['Parasitoide pupa juvenil'])
_graficar_pobs(eje4, res_todo[4]['Parasitoide larvas juvenil'])
_graficar_obs(eje, 'O. arenosella juvenil_5')
_graficar_obs(eje2, 'O. arenosella pupa')
_graficar_obs(eje3, 'Parasitoide pupa juvenil')
_graficar_obs(eje4, 'Parasitoide larvas juvenil')

eje.set_title('O. arenosella juvenil 5', fontsize=20)
eje2.set_title('O. arenosella pupa', fontsize=20)
eje3.set_title('Juvenile parasitoide pupa', fontsize=20)
eje4.set_title('Juvenile parasitoide larvas', fontsize=20)

fig.legend(
    *eje.get_legend_handles_labels(), loc='lower center', ncol=3, fontsize=20,
)
fig.subplots_adjust(bottom=0.15, wspace=0.2)
fig.savefig('Artículo 1 Fig 5.png')
