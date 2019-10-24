import math as mat
from warnings import warn as avisar

import numpy as np
from scipy import stats as estad
from scipy.special import expit, logit
from tikon.ecs._espec_dists import obt_scipy, obt_nombre, obt_prms_obj_scipy, líms_dist, clase_scipy, prms_dist
from tikon.ecs._utils import proc_líms, líms_compat
from tikon.ecs.dists.dists import Dist, _escl_inf, _dist_mu


class DistAnalítica(Dist):
    def __init__(símismo, dist, paráms, transf=None):
        símismo._escl = paráms.pop('escl') if 'escl' in paráms else 1
        símismo._ubic = paráms.pop('ubic') if 'ubic' in paráms else 0

        símismo._transf = transf

        if isinstance(dist, str):
            símismo.nombre_dist = dist
            símismo.paráms = paráms
            símismo.dist = obt_scipy(dist, paráms)
        else:
            símismo.nombre_dist = obt_nombre(dist)
            símismo.paráms = obt_prms_obj_scipy(dist)
            símismo.dist = dist

    def obt_vals(símismo, n):
        return símismo.transf_vals(símismo.dist.rvs(n))

    def obt_vals_índ(símismo, í):
        return símismo.obt_vals(n=len(í))

    def tmñ(símismo):
        return np.inf

    def aprox_líms(símismo, prc):

        # Las superficies de las colas que hay que dejar afuera del rango de los límites
        colas = ((1 - prc) / 2, 0.5 + prc / 2)

        líms_d = np.array([símismo.dist.percentiles(colas[0]), símismo.dist.percentiles(colas[1])])

        return símismo.transf_vals(líms_d)

    def transf_vals(símismo, vals):

        vals = vals * símismo._escl + símismo._ubic
        if símismo._transf is not None:
            vals = símismo._transf.transf(vals)

        return vals

    def a_dic(símismo):
        return {
            'tipo': símismo.__class__.__name__,
            '_transf': símismo._transf.a_dic() if símismo._transf else None,
            'dist': símismo.nombre_dist,
            'paráms': {'scipy': símismo.paráms, 'escl': símismo._escl, 'ubic': símismo._ubic}
        }

    @classmethod
    def de_dic(cls, dic):
        transf = TransfDist.de_dic(dic['_transf']) if dic['_transf'] else None
        return cls(dist=dic['dist'], paráms=dic['paráms'], transf=transf)

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
                    'No se puede especificar densidad de 1 con rango ilimitado como "{}".'.format(líms_dens)
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
    def de_traza(cls, trz, líms, permitidas):

        # Un diccionario para guardar el mejor ajuste
        mejor_ajuste = {}

        for nmbr in permitidas:

            # Trazas en (-∞, +∞)

            líms_d = líms_dist(nmbr)

            if líms_d[0] == -np.inf and líms_d[1] == np.inf:
                transf = _gen_transf_sin_líms(trz, líms)
                restric = {}
            elif líms_d[0] == -np.inf or líms_d[1] == np.inf:
                transf = _gen_transf_1_lím(trz, líms, líms_d)
                restric = {'floc': 0}
            else:
                transf = None

                if líms[0] == -np.inf or líms[1] == np.inf:
                    continue

                # En el caso [R, R], limitamos los valores inferiores y superiores de la distribución.
                if nmbr == 'Beta':
                    restric = {'floc': líms[0], 'fscale': líms[1] - líms[0]}
                elif nmbr == 'VonMises':
                    restric = {'floc': líms[0] + mat.pi, 'fscale': (líms[1] - líms[0]) / (2 * mat.pi)}
                else:
                    continue

            trz_transf = transf.transf_inv(trz) if transf else trz
            try:
                cls_sp = clase_scipy(nmbr)
                if nmbr == 'Uniforme':
                    prms = {'loc': líms[0], 'scale': líms[1] - líms[0]}
                else:
                    ajustados = cls_sp.fit(trz_transf, **restric)
                    prms = {pr: vl for pr, vl in zip(prms_dist(nmbr), ajustados)}
                p = estad.kstest(rvs=trz_transf, cdf=cls_sp(**prms).cdf)[1]
            except:
                prms = None
                p = 0

            # Si el ajuste es mejor que el mejor ajuste anterior...
            if not mejor_ajuste or p > mejor_ajuste['p']:
                # Guardarlo
                mejor_ajuste = dict(dist='nombre_dist', paráms=prms, transf=transf, p=p)

        if not mejor_ajuste:
            raise ValueError('No se encontró distribución permitida compatible.')

        # Si no logramos un buen aujste, avisar al usuario.
        if mejor_ajuste['p'] <= 0.10:
            avisar('El ajuste de la mejor distribución quedó muy mal (p = %f).' % round(mejor_ajuste['p'], 4))

        mejor_ajuste.pop('p')
        return DistAnalítica(**mejor_ajuste)


class TransfDist(object):
    def __init__(símismo, transf, ubic=0, escl=1):
        """

        Parameters
        ----------
        transf: str or None
        ubic: int or float
        escl: int or float
        """

        símismo._transf = transf.lower()
        if símismo._transf == 'expit':
            símismo._f = expit
            símismo._f_inv = logit
        elif símismo._transf == 'exp':
            símismo._f = np.exp
            símismo._f_inv = np.log
        elif transf is None:
            símismo._f = símismo._f_inv = lambda x: x
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

    @classmethod
    def de_dic(cls, dic):
        return TransfDist(dic['transf'], ubic=dic['ubic'], escl=dic['escl'])


def _gen_transf_sin_líms(trz, líms):
    if líms[0] == -np.inf:
        if líms[1] == np.inf:
            # noinspection PyTypeChecker
            return TransfDist(None, ubic=np.mean(trz), escl=np.std(trz))
        return TransfDist('exp', ubic=líms[1], escl=-np.std(trz))

    if líms[1] == np.inf:
        # noinspection PyTypeChecker
        return TransfDist('exp', ubic=líms[0], escl=np.std(trz))
    return TransfDist('expit', ubic=líms[0], escl=líms[1] - líms[0])


def _gen_transf_1_lím(trz, líms, líms_d):
    if sum([líms[0] == -np.inf, líms[1] == np.inf]) != 1:
        return
    if (np.isfinite(líms[0]) and np.isfinite(líms_d[0])) or (np.isfinite(líms[1]) and np.isfinite(líms_d[1])):
        escl = 1
        ubic = líms[0] - líms_d[0]
    else:
        escl = -1
        ubic = -líms[0] - líms_d[1]

    return TransfDist(None, ubic=ubic, escl=escl * np.std(trz))
