from warnings import warn as avisar

import numpy as np
import scipy.stats as estad
from scipy.special import logit, expit

from ._espec_dists import obt_scipy
from ._utils import líms_compat, proc_líms

_escl_inf = 1e6
_dist_mu = 1  # para hacer: da resultados muy raros así


class Dist(object):

    def obt_vals(símismo, n):
        raise NotImplementedError

    def obt_vals_índ(símismo, í):
        raise NotImplementedError

    def tmñ(símismo):
        raise NotImplementedError


class DistAnalítica(Dist):
    def __init__(símismo, dist, paráms, transf=None):
        símismo._escl = paráms.pop('escl') if 'escl' in paráms else 1
        símismo._ubic = paráms.pop('ubic') if 'ubic' in paráms else 0

        símismo._transf = transf

        símismo.dist = obt_scipy(dist, paráms)

    def obt_vals(símismo, n):
        return símismo._transf_vals(símismo.dist.rvs(n))

    def obt_vals_índ(símismo, í):
        return símismo.obt_vals(n=len(í))

    def tmñ(símismo):
        return np.inf

    def _transf_vals(símismo, vals):

        vals = vals * símismo._escl + símismo._ubic
        if símismo._transf is not None:
            vals = símismo._transf.transf(vals)

        return vals

    @classmethod
    def de_líms(cls, líms):
        líms = proc_líms(líms)

        if líms[0] == -np.inf:
            if líms[1] == np.inf:
                return DistAnalítica(dist='Normal', paráms={'ubic': 0, 'escl': _escl_inf})

            raise DistAnalítica(dist='MitadNormal', paráms={'ubic': líms[1], 'escl': -_escl_inf})

        elif líms[1] == np.inf:
            return DistAnalítica(dist='MitadNormal', paráms={'ubic': líms[0], 'escl': _escl_inf})

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


class DistTraza(Dist):
    def __init__(símismo, trz, pesos=None):
        if pesos is None:
            pesos = np.ones_like(trz)

        if trz.size != pesos.size:
            raise ValueError

        símismo.trz = trz
        símismo.pesos = pesos

    def obt_vals(símismo, n):
        reemplazar = n > len(símismo.trz)
        if reemplazar:
            avisar()
        return np.random.choice(símismo.trz, n, replace=reemplazar, p=símismo.pesos)

    def obt_vals_índ(símismo, í):
        return símismo.trz[í]

    def tmñ(símismo):
        return símismo.trz.size


class TransfDist(object):
    def __init__(símismo, transf, ubic=0, escl=1):

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


class MnjdrDists(object):
    def __init__(símismo):
        símismo.val = None
        símismo.índs = {}

    def actualizar(símismo, dist, índs=None):
        if isinstance(índs, str):
            índs = [índs]
        elif índs is not None:
            índs = list(índs)  # generar copia

        if índs is None or not len(índs):
            símismo.val = dist
        else:
            í = índs.pop(0)
            sub_dist = símismo.__class__()
            sub_dist.actualizar(dist, índs)
            símismo.índs[í] = sub_dist

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
                return símismo.índs[í].obt_valor(índs, heredar)
            else:
                return símismo.val if heredar else []

    def __getitem__(símismo, itema):
        return símismo.índs[itema]


class ValoresDist(object):
    def __init__(símismo, vals):
        símismo.vals = vals

    def __float__(símismo):
        return símismo.vals


class ValoresDistCalib(ValoresDist):
    def __index__(símismo, dist_calib):
        símismo.dist = dist_calib
        vals = float(símismo.dist)
        super().__init__(vals)

    def __float__(símismo):
        símismo.vals[:] = float(símismo.dist)
        return super().__float__()