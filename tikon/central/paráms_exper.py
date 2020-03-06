import numpy as np
from scipy.stats import expon, norm

from tikon.ecs import Parám
from tikon.ecs.aprioris import APrioriDens, APrioriDist
from tikon.ecs.paráms import ValsParámCoso, ValsParámCosoInter, MatrParám
from tikon.ecs.árb_coso import ParámCoso
from tikon.utils import proc_líms, EJE_PARÁMS, EJE_ESTOC, EJE_TIEMPO
from .datos import DatosVar, DatosMód


class PlantillaParámsExper(dict):
    def __init__(símismo, nombre, exper, sim, datos, n_reps):
        símismo.nombre = nombre
        símismo.exper = exper
        símismo.sim = sim
        símismo.datos = datos
        símismo.n_reps = n_reps
        super().__init__()

    def vals_paráms(símismo):
        return [val for s in símismo for val in símismo[s].vals_paráms()]

    def iniciar(símismo):
        for s in símismo:
            símismo[s].iniciar()

    def __str__(símismo):
        return símismo.nombre


class ParámsExperVar(PlantillaParámsExper):

    def __init__(símismo, nombre, exper, sim, datos, n_reps):
        super().__init__(nombre, exper, sim=sim, datos=datos, n_reps=n_reps)
        líms = proc_líms(sim.líms)
        # para hacer: estandardizar
        if símismo.datos.obs:
            ref = min(líms[1], np.nanmax([np.nanmax(o_.datos.values) for o_ in símismo.datos.obs]))
            if líms == (0, np.inf):
                apriori = APrioriDist(expon(0, ref))
            else:
                apriori = APrioriDist(norm(0, ref))
        else:
            apriori = sim.apriori

        símismo.prm = ParámInic(símismo.datos.prm, exper=exper, unids=sim.unids, líms=sim.líms, apriori=apriori)
        índs = list(sim.iter_índs(datos=sim.datos, excluir=[EJE_TIEMPO, EJE_PARÁMS, EJE_ESTOC]))
        coords = {
            dim: sim.datos.coords[dim] for dim in sim.datos.dims if dim not in [EJE_TIEMPO, EJE_PARÁMS, EJE_ESTOC]
        }

        for índ in índs:
            l_índ = list(índ.values())
            apriori_inic = símismo.datos.prm.apriori(inter=l_índ, heredar=True)
            if apriori_inic:
                símismo.prm.espec_apriori(APrioriDist(apriori_inic), inter=l_índ)
            else:
                apriori = sim.apriori_de_obs(símismo.datos.obs, índ)
                if apriori:
                    símismo.prm.espec_apriori(apriori, inter=l_índ)

        símismo.prm.de_dic(símismo.datos.prm.a_dic())

        def _gen_matr_prm(crds, índs_=None, inter=None):
            índs_ = [] if índs_ is None else índs_
            inter = inter or []
            if crds:
                eje = list(crds)[0]
                crds = dict(crds)
                índs_ = crds.pop(eje)
                cls = MatrParám if índs_ is None else ValsParámCosoInter
                return cls([
                    _gen_matr_prm(crds=crds, índs_=í, inter=inter + [í]) for í in índs_
                ], eje=eje, índice=inter[-1] if len(inter) else None
                )
            else:
                return ValsParámCoso(tmñ=símismo.n_reps, prm_base=símismo.prm, índice=índs_, inter=inter)

        símismo.matr = _gen_matr_prm(coords)

    def vals_paráms(símismo):
        return símismo.matr.vals_paráms()

    def iniciar(símismo):
        símismo.matr.act_vals()

    def a_dic(símismo):
        """No incluimos observaciones en el diccionario para guardar."""
        return símismo.prm.a_dic()

    def de_dic(símismo, d):
        símismo.prm.de_dic(d)


class ParámsExperMód(PlantillaParámsExper):

    def __init__(símismo, nombre, exper, sim, datos, n_reps):
        super().__init__(nombre, exper, sim, datos, n_reps)

        for var in símismo.sim:
            if símismo.sim[var].inicializable:
                if var not in símismo.datos:
                    símismo.datos[var] = DatosVar(var)
                datos = símismo.datos[var]
                símismo[var] = ParámsExperVar(var, exper, símismo.sim[var], datos=datos, n_reps=n_reps)


class ParámsExper(PlantillaParámsExper):

    def __init__(símismo, exper, sim):
        super().__init__(exper.nombre, exper, sim, datos=exper.datos, n_reps=sim.reps['paráms'])

        símismo.exper = exper
        for mód in símismo.sim:
            if mód not in símismo.datos:
                símismo.datos[mód] = DatosMód(mód)
            datos = símismo.datos[mód]
            símismo[mód] = ParámsExperMód(mód, exper, símismo.sim[mód], datos=datos, n_reps=símismo.n_reps)


class ParámInic(ParámCoso):

    def __init__(símismo, prm_espejo, exper, unids, líms, apriori):
        símismo.prm_espejo = prm_espejo
        nombre = prm_espejo.nombre
        atribs = {'nombre': nombre, 'unids': unids, 'líms': líms, 'apriori': apriori}
        super().__init__(pariente=type(nombre, (Parám,), atribs), coso=exper)

    def agregar_calib(símismo, id_cal, dist, inter=None):
        símismo.prm_espejo.agregar_calib(id_cal, dist, inter)
