import os
from copy import copy

from tikon.calib import gen_calibrador
from tikon.clima.clima import Clima
from tikon.ecs.dists import DistAnalítica
from tikon.estruc.tiempo import Tiempo
from tikon.exper.exper import Exper
from tikon.manejo.manejo import Manejo
from tikon.result.res import ResultadosSimul
from tikon.sensib import gen_anlzdr_sensib


class Simulador(object):

    def __init__(símismo, módulos):
        símismo._módulos = módulos

        # para hacer: combinar en un objeto
        símismo.mnjdr_móds = None  # type: MnjdrMódulos
        símismo.exper = None  # type: Exper
        símismo.tiempo = None  # type: Tiempo
        símismo.corrida = None  # type: ResultadosSimul

    def simular(
            símismo, días=None, f_inic=None, paso=1, exper=None, calibs=None, n_rep_estoc=30, n_rep_parám=30,
            vars_interés=None
    ):

        símismo.iniciar(días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám, vars_interés)
        símismo.correr()
        símismo.cerrar()

        return símismo.corrida

    def iniciar(símismo, días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám, vars_interés):

        símismo.iniciar_estruc(días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám, vars_interés)
        símismo.iniciar_vals()

    def iniciar_estruc(símismo, días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám, vars_interés, llenar=True):

        símismo.exper = exper or Exper()
        símismo.mnjdr_móds = MnjdrMódulos(símismo._módulos, símismo.exper)

        f_inic = f_inic or símismo.exper.f_inic()
        n_días = días or símismo.exper.n_días()

        símismo.tiempo = Tiempo(día=0, f_inic=f_inic, paso=paso, n_días=n_días)
        parc = símismo.mnjdr_móds.obt_val_control('parcelas')

        calibs = _gen_espec_calibs(calibs, aprioris=False, heredar=True, corresp=True)
        for m in símismo.mnjdr_móds:
            m.iniciar_estruc(símismo.tiempo, símismo.mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés)

        if llenar:
            símismo.mnjdr_móds.llenar_coefs(calibs, n_rep_parám=n_rep_parám)

    def iniciar_vals(símismo):

        símismo.mnjdr_móds.act_coefs()

        símismo.corrida = ResultadosSimul(símismo.mnjdr_móds, símismo.tiempo)
        for m in símismo.mnjdr_móds:
            m.iniciar_vals()

    def correr(símismo):
        while símismo.tiempo.avanzar():
            símismo.incrementar()

    def incrementar(símismo):
        for m in símismo.mnjdr_móds:
            m.incrementar()

        símismo.corrida.actualizar_res()

    def cerrar(símismo):
        símismo.corrida.finalizar()
        for m in símismo.mnjdr_móds:
            m.cerrar()

    def sensib(
            símismo, días=None, f_inic=None, exper=None, n=10, método='sobol', calibs=None, paso=1, n_rep_estoc=30,
            vars_interés=None, ops_mstr=None, ops_anlz=None
    ):
        ops_mstr = ops_mstr or {}
        ops_anlz = ops_anlz or {}
        calibs = _gen_espec_calibs(calibs, aprioris=True, heredar=True, corresp=False)
        anlzdr = gen_anlzdr_sensib(método, símismo.mnjdr_móds.paráms(), calibs=calibs)

        símismo.iniciar_estruc(
            días=días, f_inic=f_inic, paso=paso, exper=exper, calibs=calibs, n_rep_estoc=n_rep_estoc, n_rep_parám=1,
            vars_interés=vars_interés
        )
        anlzdr.aplicar_muestrea(n, ops=ops_mstr)
        símismo.iniciar_vals()
        símismo.correr()
        símismo.cerrar()

        return anlzdr.analizar(símismo.corrida, ops=ops_anlz)

    def calibrar(
            símismo, nombre, días=None, f_inic=None, exper=None, n_iter=300, método='epm', calibs=None,
            paso=1, n_rep_estoc=30
    ):

        def func():
            símismo.iniciar_vals()
            símismo.correr()
            return símismo.corrida.procesar_calib()

        calibs = _gen_espec_calibs(calibs, aprioris=True, heredar=True, corresp=False)

        símismo.iniciar_estruc(
            días=días, f_inic=f_inic, paso=paso, exper=exper, calibs=calibs, n_rep_estoc=n_rep_estoc, n_rep_parám=1,
            vars_interés=None, llenar=False
        )

        clbrd = gen_calibrador(método, func, símismo.mnjdr_móds.paráms(), calibs)
        clbrd.calibrar(n_iter=n_iter, nombre=nombre)

    def guardar_calib(símismo, directorio=''):
        símismo.mnjdr_móds.guardar_calib(directorio)


class MnjdrMódulos(object):
    def __init__(símismo, módulos, exper):
        if not isinstance(módulos, list):
            módulos = [módulos]
        módulos.extend([Manejo(), Clima()])

        símismo.módulos = {str(mód): mód for mód in módulos}
        símismo.exper = exper

    def obt_valor(símismo, var, mód, índs=None):
        # para hacer: ¿Necesario o simplemente emplear MnjdrMódulos['mód'].obt_valor()?
        return símismo[str(mód)].obt_valor(var, índs=índs)

    def obt_val_control(símismo, var):
        return símismo.exper.obt_control(var)

    def paráms(símismo):
        return MnjdrParámsSimul(símismo)

    def llenar_coefs(símismo, calibs, n_rep_parám):
        # para hacer: ¿separar símismo.paráms()?
        símismo.paráms().llenar_coefs(calibs, n_rep_parám=n_rep_parám)

    def act_coefs(símismo):
        for mód in símismo:
            mód.act_coefs()

    def guardar_calib(símismo, directorio=''):
        for m in símismo:
            m.guardar_calib(directorio=os.path.join(directorio, str(m)))

    def __iter__(símismo):
        for m in símismo.módulos.values():
            yield m

    def __getitem__(símismo, itema):
        return símismo.módulos[itema]


class MnjdrParámsSimul(object):
    def __init__(símismo, módulos):
        símismo._módulos = módulos
        símismo.vals_paráms = [pr for mód in módulos for pr in mód.paráms()]

    def __iter__(símismo):
        for prm in símismo.vals_paráms:
            yield prm

    def llenar_coefs(símismo, calibs, n_rep_parám):
        calibs.llenar_vals(símismo.vals_paráms, n_rep_parám)


class EspecCalibsCorrida(object):
    def __init__(símismo, calibs=None, aprioris=False, corresp=True, heredar_inter=True):
        símismo.calibs = [calibs] if isinstance(calibs, str) else calibs
        símismo.aprioris = aprioris
        símismo.corresp = corresp
        símismo.heredar_inter = heredar_inter

    def llenar_vals(símismo, l_vals_prm, n_reps):

        if símismo.aprioris:
            for vl in list(l_vals_prm):
                if vl.apriori():
                    vl.llenar_de_apriori()
            l_vals_prm = [vl for vl in l_vals_prm if not vl.apriori()]

        l_dists, corresp = símismo._filtrar_dists(l_vals_prm)

        import numpy as np
        índs_dists = {}
        for vl, d_dists in zip(l_vals_prm, l_dists):
            n_dists = len(d_dists)
            if n_dists == 0:
                vl.llenar_de_base()
            else:
                n_por_dist = np.full(n_dists, n_reps // n_dists)
                extras = n_reps % n_dists
                n_por_dist[:extras] += 1

                if corresp:
                    for í, (nmb, dist) in enumerate(d_dists.items()):
                        if nmb not in índs_dists:
                            índs_dists[nmb] = np.random.randint(dist.tmñ(), size=n_por_dist[í])
                    vl.llenar_de_dists({d_dists[nmb]: índs_dists[nmb] for nmb in d_dists})
                else:
                    vl.llenar_de_dists({dist: n for dist, n in zip(d_dists.values(), n_por_dist)})

    def gen_dists_calibs(símismo, l_vals_prm, permitidas):
        # Para hacer: limpiar TODO esto...es horriblemente inelegante
        d_dists_calib = {}

        def agregar_dist(val, dst):
            try:
                d_pre = next(d for d in d_dists_calib if any(v == val for v in d_dists_calib[d]))
                d_dists_calib[d_pre].append(val)
            except StopIteration:
                d_dists_calib[dst] = [val]

        if símismo.aprioris:
            for vl in list(l_vals_prm):
                apriori = vl.apriori()
                if apriori:
                    if apriori.nombre_dist not in permitidas:
                        raise ValueError(apriori.nombre_dist)
                    agregar_dist(vl, copy(apriori))

            l_vals_prm = [vl for vl in l_vals_prm if not any(vl in l for l in d_dists_calib.values())]

        l_dists = símismo._filtrar_dists(l_vals_prm)[0]
        import numpy as np
        for vl, d_dists in zip(l_vals_prm, l_dists):
            n_dists = len(d_dists)
            if n_dists == 0:
                dist_base = vl.dist_base()
                if dist_base.nombre_dist not in permitidas:
                    raise ValueError(dist_base.nombre_dist)
                agregar_dist(vl, copy(dist_base))
                continue
            elif n_dists == 1:
                dist = list(d_dists.values())[0]
                if isinstance(dist, DistAnalítica) and dist.nombre_dist in permitidas:
                    agregar_dist(vl, copy(dist))
                    continue

            traza = np.ravel((d.obt_vals(100) for d in d_dists.values()))
            agregar_dist(vl, DistAnalítica.de_traza(traza, permitidas))

        return d_dists_calib

    def _filtrar_dists(símismo, l_vals_prm):
        dists_disp = [pr.dists_disp(símismo.heredar_inter) for pr in l_vals_prm]

        if símismo.calibs is not None:
            for i, prm in enumerate(dists_disp):
                dists_disp[i] = {nmb: dist for nmb, dist in prm.items() if nmb in símismo.calibs}

        corresp = símismo.corresp
        if símismo.corresp:
            comunes = [
                dist for dist in set(d for prm in dists_disp for d in prm) if all(dist in prm for prm in dists_disp)
            ]
            if comunes:
                dists_disp = [{nmb: dist for nmb, dist in prm.items() if nmb in comunes} for prm in dists_disp]
            else:
                corresp = False

        return dists_disp, corresp


def _gen_espec_calibs(calibs, aprioris, heredar, corresp):
    if isinstance(calibs, EspecCalibsCorrida):
        return calibs
    else:
        return EspecCalibsCorrida(calibs, aprioris=aprioris, corresp=corresp, heredar_inter=heredar)