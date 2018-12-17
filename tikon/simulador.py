from tikon.calib import gen_calibrador
from tikon.clima import Clima
from tikon.exper import Exper
from tikon.manejo import Manejo
from tikon.rsltd.valid import Validación
from tikon.tiempo import Tiempo


class Simulador(object):

    def __init__(símismo, módulos):
        símismo._módulos = módulos
        símismo.mnjdr_móds = None  # type: MnjdrMódulos
        símismo.exper = None  # type: Exper
        símismo.tiempo = None  # type: Tiempo
        símismo.corrida = None  # type: ResultadosSimul

    def simular(símismo, días=None, f_inic=None, paso=1, exper=None, calibs=None, n_rep_estoc=30, n_rep_parám=30):

        calibs = _gen_espec_calibs(calibs, aprioris=False, heredar=True, corresp=True)

        símismo.iniciar(días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám)
        símismo.correr()
        símismo.cerrar()

        return símismo.corrida

    def iniciar(símismo, días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám):

        símismo.iniciar_estruc(días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám)
        símismo.iniciar_vals()

    def iniciar_estruc(símismo, días, f_inic, paso, exper, calibs, n_rep_estoc, n_rep_parám):

        símismo.exper = exper or Exper()
        símismo.mnjdr_móds = MnjdrMódulos(símismo._módulos, símismo.exper)

        n_días = días or símismo.exper.días()
        f_inic = f_inic or símismo.exper.f_inic()

        símismo.tiempo = Tiempo(día=0, f_inic=f_inic, paso=paso, n_días=n_días)
        parc = símismo.mnjdr_móds.obt_val_control('parcelas')

        for m in símismo.mnjdr_móds:
            m.iniciar_estruc(símismo.tiempo, símismo.mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc)

        símismo.mnjdr_móds.llenar_coefs(calibs, n_rep_parám=n_rep_parám)

    def iniciar_vals(símismo):

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
        for m in símismo.mnjdr_móds:
            m.cerrar()

    def validar(símismo, exper=None, paso=1, calibs=None, n_rep_estoc=30, n_rep_parám=30):

        símismo.simular(paso=paso, exper=exper, calibs=calibs, n_rep_estoc=n_rep_estoc, n_rep_parám=n_rep_parám)

        return Validación(símismo.corrida)

    def calibrar(símismo, exper=None, n_iter=300, método='epm', calibs=None, paso=1, n_rep_estoc=30):

        def func():
            símismo.iniciar_vals()
            símismo.correr()
            return símismo.corrida.procesar_calib()

        calibs = _gen_espec_calibs(calibs, aprioris=True, heredar=True, corresp=False)

        símismo.iniciar_estruc(
            días=None, f_inic=None, paso=paso, exper=exper, calibs=calibs, n_rep_estoc=n_rep_estoc, n_rep_parám=1
        )

        clbrd = gen_calibrador(método, func, símismo.mnjdr_móds.paráms())
        clbrd.calibrar(func, n_iter=n_iter)


class MnjdrMódulos(object):
    def __init__(símismo, módulos, exper):
        if not isinstance(módulos, list):
            módulos = [módulos]
        módulos.extend([Manejo(), Clima()])

        símismo.módulos = {str(mód): mód for mód in módulos}
        símismo.exper = exper

    def obt_valor(símismo, var, mód):
        return símismo[str(mód)].obt_valor(var)

    def obt_val_control(símismo, var):
        return símismo.exper.obt_control(var)

    def paráms(símismo):
        return MnjdrParámsSimul(símismo)

    def llenar_coefs(símismo, calibs, n_rep_parám):
        # para hacer: ¿separar símismo.paráms()?
        símismo.paráms().llenar_coefs(calibs, n_rep_parám=n_rep_parám)
        for mód in símismo:
            mód.act_coefs()

    def __iter__(símismo):
        for m in símismo.módulos.values():
            yield m

    def __getitem__(símismo, itema):
        return símismo.módulos[itema]


class MnjdrParámsSimul(object):
    def __init__(símismo, módulos):
        símismo._módulos = módulos
        símismo.vals_paráms = [pr for mód in módulos for pr in mód.paráms()]

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
        if corresp:
            raise NotImplementedError
        else:
            for vl, d_dists in zip(l_vals_prm, l_dists):
                n_dists = len(d_dists)
                if n_dists == 0:
                    vl.llenar_de_base()
                else:
                    n_por_dist = np.full(n_dists, n_reps // n_dists)
                    extras = n_reps % n_dists
                    n_por_dist[:extras] += 1

                    vl.llenar_de_dist({dist: n for dist, n in zip(d_dists, n_por_dist)})

    def gen_dists_calibs(símismo, l_vals_prm, permitidas):
        if símismo.aprioris:
            raise NotImplementedError

        l_dists = símismo._filtrar_dists(l_vals_prm)

        raise NotImplementedError

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


class ResultadosSimul(object):
    def __init__(símismo, módulos, tiempo):
        símismo.resultados = {mód: mód.resultados for mód in módulos}
        símismo.tiempo = tiempo

        símismo.datos = NotImplemented

    def reinic(símismo):
        pass

    def actualizar_res(símismo):
        for r in símismo:
            r.actualizar()

    def procesar_calib(símismo):
        pass

    def __iter__(símismo):
        for r in símismo.resultados.values():
            yield r


def _gen_espec_calibs(calibs, aprioris, heredar, corresp):
    if isinstance(calibs, EspecCalibsCorrida):
        return calibs
    else:
        return EspecCalibsCorrida(calibs, aprioris=aprioris, corresp=corresp, heredar_inter=heredar)
