from typing import Union, Optional, TypedDict, Any, cast
from warnings import warn as avisar

import numpy as np
from matplotlib.axes import Axes
from scipy import stats as estad
from scipy.special import expit, logit
from scipy.stats._continuous_distns import FitDataError
from scipy.stats._distn_infrastructure import rv_continuous_frozen
from typing_extensions import NotRequired

from tikon.ecs.dists import utils
from tikon.ecs.dists.dibs import dibujar_dist
from tikon.ecs.dists.dists import Dist, _escala_inf, _dist_mu, DicDist
from tikon.ecs.dists.utils import obt_scipy, obt_nombre, obt_prms_obj_scipy, líms_dist, clase_scipy, prms_dist, \
    proc_líms, \
    Líms_Con_None, Líms_Numéricas
from tikon.ecs.utils import líms_compat
from tikon.tipos import Tipo_Matriz_Numérica, Tipo_Matriz_Núm_Entero, Tipo_Valor_Numérico


class DicDistAnalítica(DicDist, TypedDict):
    transf: Optional["DicTransfDist"]
    paráms: tuple[tuple, Tipo_Valor_Numérico, Tipo_Valor_Numérico]
    dist: str


class DistAnalítica(Dist):
    dist: rv_continuous_frozen
    _transf: Optional["TransfDist"]
    paráms = tuple[tuple, int | float, int | float]
    líms: tuple[Tipo_Valor_Numérico, Tipo_Valor_Numérico]

    def __init__(símismo, dist: rv_continuous_frozen, transf: "TransfDist" = None):

        símismo.nombre_dist = obt_nombre(dist)
        paráms = obt_prms_obj_scipy(dist)
        if transf is None:
            prms, ubic, escl = paráms
            if ubic != 0 or escl != 1:
                dist = obt_scipy(símismo.nombre_dist, (prms, 0, 1))
                transf = TransfDist(None, ubic=ubic, escl=escl)
                paráms = (prms, 0, 1)

        símismo.dist = dist
        símismo.paráms = paráms
        símismo._transf = transf

        símismo.líms = tuple(símismo.transf_vals(np.array(líms_dist(símismo.dist))))

    def obt_vals(símismo, n: int) -> Tipo_Matriz_Numérica:
        return símismo.transf_vals(símismo.dist.rvs(n))

    def obt_vals_índ(símismo, í: Tipo_Matriz_Núm_Entero) -> Tipo_Matriz_Numérica:
        return símismo.obt_vals(n=len(í))

    def tmñ(símismo) -> Union[int, float]:
        return np.inf

    def aprox_líms(símismo, prc) -> np.ndarray[Any, np.dtype[np.number]]:

        # Las superficies de las colas que hay que dejar afuera del rango de los límites
        colas = ((1 - prc) / 2, 0.5 + prc / 2)

        líms_d = np.array([símismo.dist.ppf(colas[0]), símismo.dist.ppf(colas[1])])

        return símismo.transf_vals(líms_d)

    def transf_vals(símismo, vals: Tipo_Matriz_Numérica) -> Tipo_Matriz_Numérica:

        if símismo._transf is not None:
            vals = símismo._transf.transf(vals)

        return vals

    def dibujar(símismo, nombre=None, ejes=None, argsll=None) -> Axes:
        return dibujar_dist(símismo, nombre=nombre or símismo.nombre_dist, ejes=ejes, argsll=argsll)

    def a_dic(símismo) -> DicDistAnalítica:
        return DicDistAnalítica(
            tipo=símismo.__class__.__name__,
            transf=símismo._transf.a_dic() if símismo._transf else None,
            dist=símismo.nombre_dist,
            paráms=símismo.paráms
        )

    @classmethod
    def de_dic(cls, dic: DicDist) -> "DistAnalítica":
        if dic["tipo"] != "DistAnalítica":
            raise ValueError(dic)

        dicDistAnalítica = cast(DicDistAnalítica, dic)
        transf = TransfDist.de_dic(dicDistAnalítica['transf']) if dicDistAnalítica['transf'] else None
        dist_sp = obt_scipy(dicDistAnalítica['dist'], dicDistAnalítica['paráms'])
        return cls(dist=dist_sp, transf=transf)

    @classmethod
    def de_líms(cls, líms: Optional[Líms_Con_None]) -> "DistAnalítica":
        líms = proc_líms(líms)

        if líms[0] == -np.inf:
            if líms[1] == np.inf:
                return DistAnalítica(dist=estad.norm(), transf=TransfDist(None, ubic=0, escl=_escala_inf))

            return DistAnalítica(dist=estad.expon(), transf=TransfDist(None, ubic=líms[1], escl=-_escala_inf))

        if líms[1] == np.inf:
            return DistAnalítica(dist=estad.expon(), transf=TransfDist(None, ubic=líms[0], escl=_escala_inf))

        return DistAnalítica(dist=estad.uniform(), transf=TransfDist(None, ubic=líms[0], escl=líms[1] - líms[0]))

    @classmethod
    def de_dens(
            cls, dens: int | float, líms_dens: Optional[Líms_Con_None],
            líms: Optional[Líms_Con_None]
    ) -> "DistAnalítica":
        líms_dens_resueltas = np.array(proc_líms(líms_dens))
        líms_resueltas = np.array(proc_líms(líms))
        líms_compat(líms_dens_resueltas, líms_resueltas)

        if dens == 1:
            if np.isinf(líms_dens_resueltas[0]) or np.isinf(líms_dens_resueltas[1]):
                raise ValueError(
                    'No se puede especificar densidad de 1 con rango ilimitado como "{}".'.format(líms_dens_resueltas)
                )
            return DistAnalítica(
                dist=estad.uniform(), transf=TransfDist(None, ubic=líms_dens_resueltas[0], escl=líms_dens_resueltas[1] - líms_dens_resueltas[0])
            )
        elif dens <= 0 or dens > 1:
            raise ValueError('La densidad debe ser en (0, 1].')

        if líms_resueltas[0] == -np.inf:
            if líms_resueltas[1] == np.inf:
                transf = None
            else:
                escl = (líms_resueltas[1] - líms_dens_resueltas[1]) or ((líms_resueltas[1] - líms_dens_resueltas[0]) if líms_dens_resueltas[0] != -np.inf else 1)
                transf = TransfDist('LnExp', ubic=líms_resueltas[1], escl=-escl)

        elif líms_resueltas[1] == np.inf:
            escl = (líms_dens_resueltas[0] - líms_resueltas[0]) or ((líms_dens_resueltas[1] - líms_resueltas[0]) if líms_dens_resueltas[1] != np.inf else 1)
            transf = TransfDist('LnExp', ubic=líms_resueltas[0], escl=escl)
        else:
            transf = TransfDist('Expit', ubic=líms_resueltas[0], escl=líms_resueltas[1] - líms_resueltas[0])

        if transf is None:
            líms_dens_intern = líms_dens_resueltas
        else:
            líms_dens_intern = transf.transf_inv(líms_dens_resueltas)
            líms_dens_intern.sort()

        if líms_dens_intern[0] == -np.inf:
            if líms_dens_intern[1] == np.inf:
                raise ValueError(
                    'Rangos idénticos como {r1} y {r2} no pueden tener densidad inferior a '
                    '1.'.format(r1=líms_resueltas, r2=líms_dens_resueltas)
                )
            mu = líms_dens_intern[1] - _dist_mu
            sg = -_dist_mu / estad.norm.ppf(1 - dens)

        elif líms_dens_intern[1] == np.inf:
            mu = líms_dens_intern[0] + _dist_mu
            sg = -_dist_mu / estad.norm.ppf(1 - dens)

        else:
            mu = (líms_dens_intern[1] + líms_dens_intern[0]) / 2
            sg = (líms_dens_intern[0] - líms_dens_intern[1]) / 2 / estad.norm.ppf((1 - dens) / 2)

        return DistAnalítica(estad.norm(loc=mu, scale=sg), transf=transf)

    @classmethod
    def de_traza(cls, trz: Tipo_Matriz_Numérica, líms: Líms_Con_None, permitidas: list[str] = None):
        permitidas = permitidas or list(utils.dists)

        líms = proc_líms(líms)
        if trz.min() < líms[0] or trz.max() > líms[1]:
            raise ValueError('Valores en traza deben caber en los límites teoréticos de la distribución.')

        # Un diccionario para guardar el mejor ajuste
        class DicMejorAjuste(TypedDict):
            p: int | float
            dist: rv_continuous_frozen
            transf: TransfDist

        mejor_ajuste: DicMejorAjuste | None = None

        for nmbr in permitidas:
            líms_d = líms_dist(nmbr)
            try:
                _líms_compat_teor(líms, líms_d)
            except ValueError:
                continue

            if líms_d[0] == -np.inf and líms_d[1] == np.inf:
                transf = _gen_transf_sin_líms(trz, líms)
                restric = {}
            elif líms_d[0] == -np.inf or líms_d[1] == np.inf:
                transf = _gen_transf_1_lím(trz, líms, líms_d)
                restric = {'floc': 0}
            else:
                escl = (líms[1] - líms[0]) / (líms_d[1] - líms_d[0])
                ubic = líms[0] - líms_d[0] * escl
                transf = TransfDist(None, ubic=ubic, escl=escl)
                # En el caso [R, R], limitamos los valores inferiores y superiores de la distribución.
                restric = {'floc': 0, 'fscale': 1}

            trz_transf = transf.transf_inv(trz)

            cls_sp = clase_scipy(nmbr)
            if len(prms_dist(nmbr)) == len(restric):
                prms = {'loc': 0, 'scale': 1}
            else:
                try:
                    ajustados = cls_sp.fit(trz_transf, **restric)
                except FitDataError:
                    continue
                prms = {pr: vl for pr, vl in zip(prms_dist(nmbr), ajustados)}
            p = estad.kstest(rvs=trz_transf, cdf=cls_sp(**prms).cdf)[1]

            # Si el ajuste es mejor que el mejor ajuste anterior...
            if not mejor_ajuste or p > mejor_ajuste['p']:
                # Guardarlo
                mejor_ajuste = dict(dist=cls_sp(**prms), transf=transf, p=p)

        if not mejor_ajuste:
            raise ValueError('No se encontró distribución permitida compatible.')

        # Si no logramos un buen aujste, avisar al usuario.
        if mejor_ajuste['p'] <= 0.10:
            avisar('El ajuste de la mejor distribución quedó muy mal (p = {:.6f}).'.format(mejor_ajuste['p']))

        return DistAnalítica(dist=mejor_ajuste["dist"], transf=mejor_ajuste["transf"])


class DicTransfDist(TypedDict):
    transf: Optional[str]
    ubic: Tipo_Valor_Numérico
    escl: Tipo_Valor_Numérico


class TransfDist(object):
    def __init__(símismo, transf: Optional[str], ubic: Tipo_Valor_Numérico = 0, escl: Tipo_Valor_Numérico = 1):
        """

        Parameters
        ----------
        transf: str or None
        ubic: int or float
        escl: int or float
        """
        if transf is None:
            símismo._f = símismo._f_inv = lambda x: x
            símismo._transf = None
        else:
            símismo._transf = transf.lower()
            if símismo._transf == 'expit':
                símismo._f = expit
                símismo._f_inv = logit
            elif símismo._transf == 'lnexp':
                símismo._f = lnexp
                símismo._f_inv = invlnexp
            else:
                raise ValueError(transf)

        símismo._ubic = ubic
        símismo._escl = escl

    def transf(símismo, vals: Tipo_Matriz_Numérica) -> Tipo_Matriz_Numérica:
        return símismo._f(vals) * símismo._escl + símismo._ubic

    def transf_inv(símismo, vals: Tipo_Matriz_Numérica) -> Tipo_Matriz_Numérica:
        return símismo._f_inv((vals - símismo._ubic) / símismo._escl)

    def a_dic(símismo) -> DicTransfDist:
        return {
            'transf': símismo._transf,
            'ubic': símismo._ubic,
            'escl': símismo._escl
        }

    @classmethod
    def de_dic(cls, dic: DicTransfDist) -> "TransfDist":
        return TransfDist(dic['transf'], ubic=dic['ubic'], escl=dic['escl'])


def _gen_transf_sin_líms(trz: Tipo_Matriz_Numérica, líms: Líms_Numéricas) -> TransfDist:
    if líms[0] == -np.inf:
        if líms[1] == np.inf:
            # noinspection PyTypeChecker
            return TransfDist(None, ubic=np.mean(trz), escl=np.std(trz))
        return TransfDist('LnExp', ubic=líms[1], escl=-np.std(trz))

    if líms[1] == np.inf:
        # noinspection PyTypeChecker
        return TransfDist('LnExp', ubic=líms[0], escl=np.std(trz))
    return TransfDist('Expit', ubic=líms[0], escl=líms[1] - líms[0])


def _gen_transf_1_lím(trz: Tipo_Matriz_Numérica, líms: Líms_Numéricas, líms_d: Líms_Numéricas) -> TransfDist:
    if líms_d[0] == -np.inf:
        líms_d = (-líms_d[1], np.inf)
        líms = (-líms[1], -líms[0])

    if líms[0] == -np.inf:
        escl = trz.std()
        ubic = líms[1] - líms_d[0] * escl
        return TransfDist(None, ubic=ubic, escl=-escl)
    elif líms[1] == np.inf:
        escl = trz.std()
        ubic = líms[0] - líms_d[0] * escl
        return TransfDist(None, ubic=ubic, escl=escl)

    raise ValueError(líms)


def lnexp(x: Tipo_Matriz_Numérica) -> Tipo_Matriz_Numérica:
    return np.log(np.exp(x) + 1)


def invlnexp(x: Tipo_Matriz_Numérica) -> Tipo_Matriz_Numérica:
    return np.where(x >= 50, x, np.log(np.exp(x) - 1))


def _líms_compat_teor(líms: Líms_Con_None, ref: Líms_Con_None) -> None:
    líms = proc_líms(líms)
    ref = proc_líms(ref)
    suma = sum([ref[0] == -np.inf, ref[1] == np.inf])
    if suma == 1 and sum([líms[0] == -np.inf, líms[1] == np.inf]) != 1:
        raise ValueError
    elif suma == 0 and (líms[0] == -np.inf or líms[1] == np.inf):
        raise ValueError
