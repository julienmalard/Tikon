from warnings import warn as avisar

import numpy as np
from scipy import stats as estad
from scipy.special import expit, logit
from tikon.ecs.dists.dists import Dist, _escl_inf, _dist_mu
from tikon.ecs.utils import líms_compat
from tikon.utils import proc_líms

from .utils import obt_scipy, obt_nombre, obt_prms_obj_scipy, líms_dist, clase_scipy, prms_dist


class DistAnalítica(Dist):
    def __init__(símismo, dist, paráms=None, transf=None):
        paráms = paráms or {}

        símismo._transf = transf

        if isinstance(dist, str):
            símismo.nombre_dist = dist
            símismo.paráms = paráms or []
            símismo.dist = obt_scipy(dist, paráms)
        else:
            símismo.nombre_dist = obt_nombre(dist)
            símismo.paráms = obt_prms_obj_scipy(dist)
            símismo.dist = dist

        símismo.líms = tuple(símismo.transf_vals(np.array(líms_dist(símismo.dist))))

    def obt_vals(símismo, n):
        return símismo.transf_vals(símismo.dist.rvs(n))

    def obt_vals_índ(símismo, í):
        return símismo.obt_vals(n=len(í))

    def tmñ(símismo):
        return np.inf

    def aprox_líms(símismo, prc):

        # Las superficies de las colas que hay que dejar afuera del rango de los límites
        colas = ((1 - prc) / 2, 0.5 + prc / 2)

        líms_d = np.array([símismo.dist.ppf(colas[0]), símismo.dist.ppf(colas[1])])

        return símismo.transf_vals(líms_d)

    def transf_vals(símismo, vals):

        if símismo._transf is not None:
            vals = símismo._transf.transf(vals)

        return vals

    def a_dic(símismo):
        return {
            'tipo': símismo.__class__.__name__,
            '_transf': símismo._transf.a_dic() if símismo._transf else None,
            'dist': símismo.nombre_dist,
            'paráms': símismo.paráms
        }

    @classmethod
    def de_dic(cls, dic):
        transf = TransfDist.de_dic(dic['_transf']) if dic['_transf'] else None
        dist_sp = obt_scipy(dic['dist'], dic['paráms'])
        return cls(dist=dist_sp, transf=transf)

    @classmethod
    def de_líms(cls, líms):
        líms = proc_líms(líms)

        if líms[0] == -np.inf:
            if líms[1] == np.inf:
                return DistAnalítica(dist='Normal', transf=TransfDist(None, ubic=0, escl=_escl_inf))

            return DistAnalítica(dist='Exponencial', transf=TransfDist(None, ubic=líms[1], escl=-_escl_inf))

        if líms[1] == np.inf:
            return DistAnalítica(dist='Exponencial', transf=TransfDist(None, ubic=líms[0], escl=_escl_inf))

        return DistAnalítica(dist='Uniforme', transf=TransfDist(None, ubic=líms[0], escl=líms[1] - líms[0]))

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
            return DistAnalítica(dist='Uniforme', paráms={'loc': líms_dens[0], 'scale': líms_dens[1] - líms_dens[0]})
        elif dens <= 0 or dens > 1:
            raise ValueError('La densidad debe ser en (0, 1].')

        if líms[0] == -np.inf:
            if líms[1] == np.inf:
                transf = None
            else:
                transf = TransfDist('LnExp', ubic=líms[1], escl=-1)

        elif líms[1] == np.inf:
            transf = TransfDist('LnExp', ubic=líms[0])
        else:
            transf = TransfDist('Expit', ubic=líms[0], escl=líms[1] - líms[0])

        if transf is None:
            líms_dens_intern = líms_dens
        else:
            líms_dens_intern = transf.transf_inv(líms_dens)
            líms_dens_intern.sort()

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

        return DistAnalítica('Normal', paráms={'loc': mu, 'scale': sg}, transf=transf)

    @classmethod
    def de_traza(cls, trz, líms, permitidas):

        líms = proc_líms(líms)
        if trz.min() < líms[0] or trz.max() > líms[1]:
            raise ValueError('Valores en traza deben caber en los límites teoréticos de la distribución.')

        # Un diccionario para guardar el mejor ajuste
        mejor_ajuste = {}

        for nmbr in permitidas:
            líms_d = líms_dist(nmbr)
            try:
                líms_compat(líms, líms_d)
            except ValueError:
                continue

            if líms_d[0] == -np.inf and líms_d[1] == np.inf:
                transf = _gen_transf_sin_líms(trz, líms)
                restric = {}
            elif líms_d[0] == -np.inf or líms_d[1] == np.inf:
                transf = _gen_transf_1_lím(trz, líms, líms_d)
                restric = {'floc': 0}
            else:
                transf = TransfDist(None, ubic=líms[0] - líms_d[0], escl=(líms[1] - líms[0]) / (líms_d[1] - líms_d[0]))
                # En el caso [R, R], limitamos los valores inferiores y superiores de la distribución.
                restric = {'floc': 0, 'fscale': 1}

            trz_transf = transf.transf_inv(trz) if transf else trz
            try:
                cls_sp = clase_scipy(nmbr)
                if len(prms_dist(nmbr)) == len(restric):
                    prms = {'loc': 0, 'scale': 1}
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
                mejor_ajuste = dict(dist=nmbr, paráms=prms, transf=transf, p=p)

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
        if transf is None:
            símismo._f = símismo._f_inv = lambda x: x
        else:
            símismo._transf = transf.lower()
            if símismo._transf == 'expit':
                símismo._f = expit
                símismo._f_inv = logit
            elif símismo._transf == 'lnexp':
                símismo._f = lnexp
                símismo._f_inv = invlnexp
            elif símismo._transf == 'neglnexp':
                símismo._f = neglnexp
                símismo._f_inv = invneglnexp
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
            'loc': símismo._ubic, 'scale': símismo._escl
        }

    @classmethod
    def de_dic(cls, dic):
        return TransfDist(dic['transf'], ubic=dic['loc'], escl=dic['scale'])


def _gen_transf_sin_líms(trz, líms):
    if líms[0] == -np.inf:
        if líms[1] == np.inf:
            # noinspection PyTypeChecker
            return TransfDist(None, ubic=np.mean(trz), escl=np.std(trz))
        return TransfDist('LnExp', ubic=líms[1], escl=-np.std(trz))

    if líms[1] == np.inf:
        # noinspection PyTypeChecker
        return TransfDist('LnExp', ubic=líms[0], escl=np.std(trz))
    return TransfDist('Expit', ubic=líms[0], escl=líms[1] - líms[0])


def _gen_transf_1_lím(trz, líms, líms_d):
    if líms_d[0] == -np.inf:
        escl = -1
        líms_d = (-líms_d[1], np.inf)
        líms = (-líms[1], -líms[0])
    else:
        escl = 1
    ubic = líms[0] - líms_d[0]
    if líms[1] == np.inf:
        return TransfDist(None, ubic=ubic, escl=escl)
    return TransfDist('NegLnExp', ubic=ubic, escl=escl * (líms[1] - líms[0]))


def lnexp(x):
    return np.log(np.exp(x) + 1)


def invlnexp(x):
    return np.log(np.exp(x) - 1)


def neglnexp(x):
    return -np.log(np.exp(-x) + 1) / np.log(2) + 1


def invneglnexp(x):
    return -np.log(np.exp(np.log(2) * (1 - x)) - 1)
