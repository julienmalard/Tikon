from warnings import warn as avisar

import matplotlib.pyplot as dib
import numpy as np
import pymc
import scipy.stats as estad

import tikon.Matemáticas.Distribuciones as Ds
import tikon.Matemáticas.Incert as Inc

"""
Un módulo de pruebas, un poco inelegante.
"""

# Pruebas para el convertidor de distribuciones SciPy a PyMC en NuevoIncert

n_rep = 10000

dibujar = False

con_errores = []

# dists = Ds.dists.items()
dists = {'NormalTrunc': Ds.dists['NormalTrunc']}

for nombre, dist in sorted(dists.items()):

    if dist['tipo'] != 'cont':
        continue

    if dist['scipy'] is None or dist['pymc'] is None:
        continue

    mín, máx = dist['límites']
    if mín == -np.inf:
        if máx == np.inf:
            núms = estad.norm.rvs(10, 20, size=100)
        else:
            avisar('No se pudo comprobar la distribución "%s".' % nombre)
            continue

    else:
        if máx == np.inf:
            núms = estad.gamma.rvs(1, loc=mín, size=100)
        else:
            núms = estad.uniform.rvs(mín, máx-mín, size=100)

    dist_scipy = Inc.ajustar_dist(datos=núms, límites=dist['límites'], cont=True,
                                  lista_dist=[nombre])[0]
    puntos_scipy = dist_scipy.rvs(size=n_rep)

    dist_pymc = Inc.ajustar_dist(datos=núms, límites=dist['límites'], cont=True, usar_pymc=True,
                                 nombre=nombre, lista_dist=[nombre])[0]
    if isinstance(dist_pymc, pymc.Stochastic):
        puntos_pymc = np.array([dist_pymc.rand() for _ in range(n_rep)])
    elif isinstance(dist_pymc, pymc.Deterministic):
        puntos_pymc = np.empty(n_rep)
        dist_pariente = min(dist_pymc.extended_parents)
        for i in range(n_rep):
            dist_pariente.rand()
            puntos_pymc[i] = dist_pymc.value
    else:
        raise ValueError

    scipy_de_pymc = Inc.ajustar_dist(datos=puntos_pymc, límites=dist['límites'], cont=True,
                                     lista_dist=[nombre])[0]

    if dibujar:

        dib.hist(núms, normed=True, color='red', histtype='stepfilled', alpha=0.2, bins=100)

        dib.hist(puntos_scipy, normed=True, color='blue', histtype='stepfilled', alpha=0.2, bins=100)

        dib.hist(puntos_pymc, normed=True, color='green', histtype='stepfilled', alpha=0.2, bins=100)

        x = np.linspace(dist_scipy.ppf(0.01), dist_scipy.ppf(0.99), 100)
        dib.plot(x, dist_scipy.pdf(x), 'b-', lw=2, alpha=0.6)
        dib.plot(x, scipy_de_pymc.pdf(x), 'g-', lw=2, alpha=0.6)

        dib.title(nombre)
        dib.show()

    error = 0.0
    for n, i in enumerate(scipy_de_pymc.args):
        if i == 0:
            e = i - dist_scipy.args[n]
        else:
            e = (i - dist_scipy.args[n]) / dist_scipy.args[n]
        error = max(error, abs(e))

    if error >= 0.025:
        mensaje = '¡¡¡Panica!!! Hay un gran error terrible.'
        con_errores.append(nombre)
    else:
        mensaje = 'Todo bien.'

    print(nombre, error, mensaje, dist_scipy.args, scipy_de_pymc.args)

if len(con_errores):
    print('Verificar:', con_errores)
else:
    print('¡Todas las distribuciones pasaron! Todas nuestras felicitaciones, en Tamil, para ti: வாழ்த்துக்கள்!')

# Arreglar: Errores con T, TNo, etc...
