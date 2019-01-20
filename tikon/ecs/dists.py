from warnings import warn as avisar

import numpy as np
import scipy.stats as estad
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura
from scipy.special import logit, expit

from ._espec_dists import obt_scipy
from ._utils import líms_compat, proc_líms

_escl_inf = 1e10
_dist_mu = 1  # para hacer: da resultados muy raros así


class Dist(object):

    def obt_vals(símismo, n):
        raise NotImplementedError

    def obt_vals_índ(símismo, í):
        raise NotImplementedError

    def tmñ(símismo):
        raise NotImplementedError

    def aprox_líms(símismo, prc):
        raise NotImplementedError

    def a_dic(símismo):
        raise NotImplementedError

    def dibujar(símismo, ejes=None, color='#99CC00', nombre=None, rango=None):
        if ejes is None:
            fig = Figura()
            TelaFigura(fig)
            ejes = fig.add_subplot(111)
        else:
            fig = None

        n = 10000
        puntos = símismo.obt_vals(n)
        # para hacer: ¿para módulo dibujar?
        # Crear el histograma
        y, delim = np.histogram(puntos, density=True, bins=n // 100)
        x = 0.5 * (delim[1:] + delim[:-1])

        # Dibujar el histograma
        ejes.plot(x, y, 'b-', lw=2, color=color, alpha=0.6, labels=nombre)

        # Resaltar un rango, si necesario
        if rango is not None:
            if rango[1] < rango[0]:
                rango = (rango[1], rango[0])
            en_rango = (rango[0] <= x) & (x <= rango[1])
            ejes.fill_between(x[en_rango], 0, y[en_rango], color=color, alpha=0.2)

        return fig, ejes


class DistAnalítica(Dist):
    def __init__(símismo, dist, paráms, transf=None):
        símismo._escl = paráms.pop('escl') if 'escl' in paráms else 1
        símismo._ubic = paráms.pop('ubic') if 'ubic' in paráms else 0

        símismo._transf = transf

        símismo.nombre_dist = dist
        símismo.paráms = paráms
        símismo.dist = obt_scipy(dist, paráms)

    def obt_vals(símismo, n):
        return símismo.transf_vals(símismo.dist.rvs(n))

    def obt_vals_índ(símismo, í):
        return símismo.obt_vals(n=len(í))

    def tmñ(símismo):
        return np.inf

    def aprox_líms(símismo, prc):

        # Las superficies de las colas que hay que dejar afuera del rango de los límites
        colas = ((1 - prc) / 2, 0.5 + prc / 2)

        líms_dist = np.array([símismo.dist.percentiles(colas[0]), símismo.dist.percentiles(colas[1])])

        return símismo.transf_vals(líms_dist)

    def transf_vals(símismo, vals):

        vals = vals * símismo._escl + símismo._ubic
        if símismo._transf is not None:
            vals = símismo._transf.transf(vals)

        return vals

    def a_dic(símismo):
        return {
            '_transf': símismo._transf.a_dic() if símismo._transf else None,
            'dist': símismo.nombre_dist,
            'paráms': {**símismo.paráms, 'escl': símismo._escl, 'ubic': símismo._ubic}
        }

    @classmethod
    def de_líms(cls, líms):
        líms = proc_líms(líms)

        if líms[0] == -np.inf:
            if líms[1] == np.inf:
                return DistAnalítica(dist='Normal', paráms={'ubic': 0, 'escl': _escl_inf})

            return DistAnalítica(dist='Exponencial', paráms={'ubic': líms[1], 'escl': -_escl_inf})

        if líms[1] == np.inf:
            return DistAnalítica(dist='Exponencial', paráms={'ubic': líms[0], 'escl': _escl_inf})

        return DistAnalítica(dist='Uniforme', paráms={'ubic': líms[0], 'escl': líms[1] - líms[0]})

    @classmethod
    def de_dens(cls, dens, líms_dens, líms):
        líms_dens = np.array(proc_líms(líms_dens))
        líms = np.array(proc_líms(líms))
        líms_compat(líms_dens, líms)

        if dens == 1:
            if np.isinf(líms_dens[0]) or np.isinf(líms_dens[1]):
                raise ValueError(
                    'No se puede especificar densidad de 1 con rango illimitado como "{}".'.format(líms_dens)
                )
            return DistAnalítica(dist='Uniforme', paráms={'ubic': líms_dens[0], 'escl': líms_dens[1] - líms_dens[0]})
        elif dens <= 0:
            raise ValueError('La densidad debe ser en (0, 1].')

        if líms[0] == -np.inf:
            if líms[1] == np.inf:
                transf = None
            else:
                transf = TransfDist('Exp', ubic=líms[1], escl=-1)

        elif líms[1] == np.inf:
            transf = TransfDist('Exp', ubic=líms[0])
        else:
            transf = TransfDist('Expit', ubic=líms[0], escl=líms[1] - líms[0])

        if transf is None:
            líms_dens_intern = líms_dens
        else:
            líms_dens_intern = transf.transf_inv(líms_dens)

        if líms_dens_intern[0] == -np.inf:
            if líms_dens_intern[1] == np.inf:
                raise ValueError(
                    'Rangos idénticos como {r1} y {r2} no pueden tener densidad inferior a '
                    '1.'.format(r1=líms, r2=líms_dens)
                )
            else:
                mu = líms_dens_intern[1] - _dist_mu
                sg = -_dist_mu / estad.norm.ppf(1 - dens)

        elif líms_dens_intern[1] == np.inf:
            mu = líms_dens_intern[0] + _dist_mu
            sg = -_dist_mu / estad.norm.ppf(1 - dens)

        else:
            mu = (líms_dens_intern[1] + líms_dens_intern[0]) / 2
            sg = (líms_dens_intern[0] - líms_dens_intern[1]) / 2 / estad.norm.ppf((1 - dens) / 2)

        return DistAnalítica('Normal', paráms={'ubic': mu, 'escl': sg}, transf=transf)

    @classmethod
    def de_traza(cls, trz, permitidas):

        # Un diccionario para guardar el mejor ajuste
        mejor_ajuste = dict(prms={}, tipo='', p=0.0)

        dists_potenciales = [x for x in dists_potenciales if x in cls.dists_disp()]

        # Verificar que todavia queden distribuciones para considerar.
        if len(dists_potenciales) == 0:
            raise ValueError('Ninguna de las distribuciones especificadas es apropiada para el tipo de distribución.')

        # Para cada distribución potencial para representar a nuestros datos...
        for nombre_dist in dists_potenciales:

            # El diccionario de la distribución
            dic_dist = Ds.dists[nombre_dist]

            # El máximo y el mínimo de la distribución
            mín_dist, máx_dist = dic_dist['límites']

            # Verificar que los límites del parámetro y de la distribución sean compatibles
            lím_igual = (((mín_dist == mín_parám == -np.inf) or
                          (not np.isinf(mín_dist) and not np.isinf(mín_parám))) and
                         ((máx_dist == máx_parám == np.inf) or
                          (not np.isinf(máx_dist) and not np.isinf(máx_parám))))

            # Si son compatibles...
            if lím_igual:

                if mín_parám == -np.inf and máx_parám != np.inf:
                    inv = True
                else:
                    inv = False

                # Restringimos las posibilidades para las distribuciones a ajustar, si necesario
                if np.isinf(mín_parám):

                    if np.isinf(máx_parám):
                        # Para el caso de un parámetro sín límites teoréticos (-inf, inf), no hay restricciones en la
                        # distribución.
                        restric = {}

                    else:
                        raise ValueError('No debería ser posible llegar hasta este error.')
                else:

                    if np.isinf(máx_parám):
                        # En el caso [R, inf), limitamos el valor inferior de la distribución al límite inferior del
                        # parámetro
                        restric = {'floc': mín_parám}

                    else:
                        # En el caso [R, R], limitamos los valores inferiores y superiores de la distribución.
                        if nombre_dist == 'Uniforme' or nombre_dist == 'Beta':
                            restric = {'floc': mín_parám, 'fscale': máx_parám - mín_parám}
                        elif nombre_dist == 'NormalTrunc':
                            restric = {'floc': (máx_parám + mín_parám) / 2}
                        elif nombre_dist == 'VonMises':
                            restric = {'floc': mín_parám + mat.pi, 'fscale': máx_parám - mín_parám}
                        else:
                            raise ValueError(nombre_dist)

                # Ajustar los parámetros de la distribución SciPy para caber con los datos.
                if nombre_dist == 'Uniforme':
                    # Para distribuciones uniformes, no hay nada que calibrar.
                    prms = {'ubic': restric['floc'], 'escl': restric['fscale']}
                else:
                    try:
                        tupla_prms = dic_dist['scipy'].fit(datos, **restric)
                        l_prms = dic_dist['paráms']
                        prms = {p: v for p, v in zip(l_prms, tupla_prms)}
                    except:
                        prms = None

                if prms is not None:
                    # Medir el ajuste de la distribución
                    prms_scipy = prms.copy()
                    prms_scipy['loc'] = prms_scipy.pop('ubic')
                    prms_scipy['scale'] = prms_scipy.pop('escl')
                    p = estad.kstest(rvs=datos, cdf=dic_dist['scipy'](**prms_scipy).cdf)[1]

                    # Si el ajuste es mejor que el mejor ajuste anterior...
                    if p > mejor_ajuste['p'] or mejor_ajuste['tipo'] == '':
                        # Guardarlo
                        mejor_ajuste['p'] = p
                        mejor_ajuste['prms'] = prms
                        mejor_ajuste['tipo'] = nombre_dist

                        # Inversar la distribución sinecesario
                        if inv and 'escl' in prms:
                            prms['escl'] = -prms['escl']

        # Si no logramos un buen aujste, avisar al usuario.
        if mejor_ajuste['p'] <= 0.10:
            avisar('El ajuste de la mejor distribución quedó muy mal (p = %f).' % round(mejor_ajuste['p'], 4))
            # Para hacer: ¿Permitir transformaciones adicionales a los datos?

        # Devolver la distribución con el mejor ajuste, tanto como el valor de su ajuste.
        resultado = {'dist': VarSciPy(tipo_dist=mejor_ajuste['tipo'], paráms=mejor_ajuste['prms']),
                     'nombre': mejor_ajuste['tipo'],
                     'prms': mejor_ajuste['prms'],
                     'p': mejor_ajuste['p']}

        return resultado


class DistTraza(Dist):
    def __init__(símismo, trz, pesos=None):
        if pesos is None:
            pesos = np.ones_like(trz)
        else:
            pesos = pesos / np.sum(pesos)

        if trz.size != pesos.size:
            raise ValueError

        símismo.trz = trz
        símismo.pesos = pesos

    def obt_vals(símismo, n):
        reemplazar = n > len(símismo.trz)
        if reemplazar:
            avisar('Repitiendo valores porque se pidieron más repeticiones que hay disponibles.')
        return np.random.choice(símismo.trz, n, replace=reemplazar, p=símismo.pesos)

    def obt_vals_índ(símismo, í):
        return símismo.trz[í]

    def tmñ(símismo):
        return símismo.trz.size

    def aprox_líms(símismo, prc):
        # Las superficies de las colas que hay que dejar afuera del rango de los límites
        colas = ((1 - prc) / 2, 0.5 + prc / 2)

        return np.array([np.percentile(símismo.trz, colas[0] * 100, np.percentile(símismo.trz, colas[1] * 100))])

    def a_dic(símismo):
        return {
            'trz': símismo.trz,
            'pesos': símismo.pesos
        }


class TransfDist(object):
    def __init__(símismo, transf, ubic=0, escl=1):

        símismo._transf = transf
        if transf == 'Expit':
            símismo._f = expit
            símismo._f_inv = logit
        elif transf == 'Exp':
            símismo._f = np.exp
            símismo._f_inv = np.log
        else:
            raise ValueError(transf)

        símismo._ubic = ubic
        símismo._escl = escl

    def transf(símismo, vals):
        return símismo._f(vals) * símismo._escl + símismo._ubic

    def transf_inv(símismo, vals):
        return símismo._f_inv((vals - símismo._ubic) / símismo._escl)

    def a_dic(símismo):
        return {
            'transf': símismo._transf,
            'ubic': símismo._ubic, 'escl': símismo._escl
        }


class MnjdrDists(object):
    def __init__(símismo):
        símismo.val = None
        símismo.índs = {}

    def actualizar(símismo, dist, índs=None):
        if isinstance(índs, str):
            índs = [índs]
        elif índs is not None:
            índs = list(índs)  # generar copia

        if índs is None or not índs:
            símismo.val = dist
        else:
            í = índs.pop(0)

            if í not in símismo.índs:
                símismo.índs[í] = MnjdrDists()

            símismo.índs[í].actualizar(dist, índs)

    def obt_val(símismo, índs=None, heredar=True):

        if isinstance(índs, str):
            índs = [índs]
        elif índs is not None:
            índs = list(índs)  # generar copia

        if índs is None or not len(índs):
            return símismo.val
        else:
            í = índs.pop(0)
            if í in símismo.índs:
                return símismo.índs[í].obt_val(índs, heredar)
            return símismo.val if heredar else []

    def __getitem__(símismo, itema):
        return símismo.índs[itema]

    def a_dic(símismo):
        return {
            'val': símismo.val.a_dic() if símismo.val else None,
            'índs': {str(ll): v.a_dic() for ll, v in símismo.índs.items()}
        }
