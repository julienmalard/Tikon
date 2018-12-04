import numpy as np

from .utils import probs_conj
from ..orgs.ecs import ecs_etps_orgs


class MnjdrEcsRed(object):
    def __init__(símismo, etapas, calibs, n_rep_paráms):
        símismo._etapas = etapas
        d_categs = {
            'Edad': CategEdad,
            'Depredación': CategDepred,
            'Crecimiento': CategCrec,
            'Reproducción': CategReprod,
            'Muertes': CategMuertes,
            'Transiciones': CategTransiciones,
            'Movimiento': CategMovimiento,
            'Estoc': CategEstoc
        }
        símismo._categs = {
            ctg: cls_ctg(ctg, ecs_etps_orgs, etapas=_etps_activas(etapas, ctg)) for ctg, cls_ctg in d_categs.items()
        }
        símismo._gen_coefs(calibs, n_rep_paráms)
        símismo.paráms =

    def etapas_categ(símismo, categ):
        return símismo[categ].etapas

    def _gen_coefs(símismo, calibs, n_rep_paráms):
        pass


    def __getitem__(símismo, itema):
        return símismo._categs[itema]


class CategEcsSimul(object):
    def __init__(símismo, nombre, árbol_ecs, etapas):
        símismo.etapas = etapas
        símismo.nombre = nombre

        símismo._subcategs = {}
        for sub in árbol_ecs[nombre]:
            etps_sub =
            if len(etps_sub):
                símismo._subcategs[str(sub)] =

    def evaluar(símismo, paso):
        for sub in símismo._subcategs.values():
            sub.evaluar(paso)

        símismo.postproc(paso)

    def postproc(símismo, paso):
        pass

    def __getitem__(símismo, itema):
        return símismo._subcategs[itema]


class CategDepred(CategEcsSimul):

    def postproc(símismo, paso):
        depred = símismo._res.obt_valor()

        # Reemplazar valores NaN con 0.
        depred[np.isnan(depred)] = 0

        # Arreglar errores de redondeo en la computación
        depred[depred < 0] = 0

        # Ajustar por superficies
        np.multiply(depred, extrn['superficies'].reshape(depred.shape[0], 1, 1, 1, 1), out=depred)

        # Convertir depredación potencial por depredador a depredación potencial total (multiplicar por la población
        # de cada depredador). También multiplicamos por el paso de la simulación. 'depred' ahora está en unidades
        # del número total de presas comidas por cada tipo de depredador por unidad de tiempo.
        np.multiply(depred, np.multiply(pobs, paso)[..., np.newaxis], out=depred)

        # Ajustar por la presencia de varios depredadores (eje = depredadores)
        eje_depredador = símismo._res.í_eje('etapa')
        probs_conj(depred, pesos=1, máx=pobs, eje=eje_depredador)

        depred[np.isnan(depred)] = 0

        # Redondear (para evitar de comer, por ejemplo, 2 * 10^-5 moscas). NO usamos la función "np.round()", porque
        # esta podría darnos valores superiores a los límites establecidos por probs_conj() arriba.
        np.floor(depred, out=depred)


class CategEstoc(CategEcsSimul):
    def postproc(símismo, paso):
        estoc = símismo._res.obt_valor()
        np.multiply(pobs, estoc, out=estoc)
        np.maximum(1, estoc, out=estoc)
        np.round(np.random.normal(0, estoc), out=estoc)

        # Verificar que no quitamos más que existen
        estoc[:] = np.where(-estoc > pobs, -pobs, estoc)


class SubCategEcsSimul(object):
    def __init__(símismo, ecs, res):
        símismo._ecs = ecs
        símismo._res = res

    def evaluar(símismo, paso):
        for ec in símismo._ecs:
            ec.evaluar(paso, res=símismo._res)


class EcSimul(object):
    def __init__(símismo, func, paráms, í_etapas):
        símismo.func = func
        símismo.paráms = paráms
        símismo.í_etapas = í_etapas

    def evaluar(símismo, paso, res):
        val = símismo.func(paráms=símismo.paráms, paso=paso, mód=mód)
        res.poner_val(val, símismo.í_etapas)


class ParámsEc(object):
    def __init__(símismo, paráms):


class MatrValoresParám(object):
    def __init__(símismo, dists):
        símismo.dists = dists
        símismo.vals = np.array(dists, dtype=float)

    def __float__(símismo):
        símismo.vals[:] = símismo.dists
        return símismo.vals
