import numpy as np
from tikon.ecs import Parám
from tikon.ecs.aprioris import APrioriDens, APrioriDist
from tikon.ecs.paráms import ValsParámCoso, ValsParámCosoInter, MatrParám
from tikon.ecs.árb_coso import ParámCoso
from tikon.utils import proc_líms, EJE_PARÁMS, EJE_ESTOC, EJE_TIEMPO


class PlantillaParámsExper(dict):
    def __init__(símismo, nombre, sim, datos, n_reps):
        símismo.nombre = nombre
        símismo.sim = sim
        símismo.datos = datos
        símismo.n_reps = n_reps
        super().__init__()

    def vals_paráms(símismo):
        return [val for s in símismo for val in símismo[s].vals_paráms()]

    def iniciar(símismo):
        for s in símismo:
            símismo[s].iniciar()

    def a_dic(símismo):
        return {ll: símismo[ll].a_dic() for ll in símismo}

    def de_dic(símismo, dic):
        for ll, d in dic.items():
            if ll in símismo:
                sub = símismo[ll]
            else:
                símismo[ll] = símismo._sub_cls(ll)
                sub = símismo[ll]
            sub.de_dic(d)

    @property
    def _sub_cls(símismo):
        raise NotImplementedError

    def __str__(símismo):
        return símismo.nombre


class ParámsExperVar(PlantillaParámsExper):
    _sub_cls = None

    def __init__(símismo, nombre, sim, datos, n_reps):
        super().__init__(nombre, sim=sim, datos=datos, n_reps=n_reps)
        if símismo.datos.obs:
            líms = proc_líms(sim.líms)
            mín = líms[0]
            máx = min(líms[1], np.max([o_.datos.values.max() for o_ in símismo.datos.obs]))
            apriori = APrioriDens((mín, máx), 0.95)
        else:
            apriori = None

        símismo.prm = ParámInic(símismo.nombre, unids=sim.unids, líms=sim.líms, apriori=apriori)
        índs = list(sim.iter_índs(datos=sim.datos, excluir=[EJE_TIEMPO, EJE_PARÁMS, EJE_ESTOC]))
        coords = {dim: sim.datos[dim].values for dim in sim.datos.dims if
                  dim not in [EJE_TIEMPO, EJE_PARÁMS, EJE_ESTOC]}

        for índ in índs:
            l_índ = list(índ.values())
            apriori_inic = símismo.datos.dists.obt_val(l_índ, heredar=True)
            if apriori_inic:
                símismo.prm.espec_apriori(APrioriDist(apriori_inic), inter=l_índ)

        def _gen_matr_prm(crds, índs=None, inter=None):
            índs = [] if índs is None else índs
            inter = inter or []
            if crds:
                eje = list(crds)[0]
                crds = dict(crds)
                índs = crds.pop(eje)
                cls = MatrParám if índs is None else ValsParámCosoInter
                return cls([
                    _gen_matr_prm(crds=crds, índs=í, inter=inter + [í]) for í in índs
                ], eje=eje, índice=inter[-1] if len(inter) else None
                )
            else:
                return ValsParámCoso(tmñ=símismo.n_reps, prm_base=símismo.prm, índice=índs, inter=inter)

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
    _sub_cls = ParámsExperVar

    def __init__(símismo, nombre, sim, datos, n_reps):
        super().__init__(nombre, sim, datos, n_reps)

        for var in símismo.sim:
            if símismo.sim[var].inicializable:
                if símismo.datos and var in símismo.datos:
                    datos = símismo.datos[var]
                    símismo[var] = ParámsExperVar(var, símismo.sim[var], datos=datos, n_reps=n_reps)


class ParámsExper(PlantillaParámsExper):
    _sub_cls = ParámsExperMód

    def __init__(símismo, exper, sim):
        super().__init__(exper.nombre, sim, datos=exper.datos, n_reps=sim.reps['paráms'])

        símismo.exper = exper
        for mód in símismo.sim:
            if símismo.datos and mód in símismo.datos:
                datos = símismo.datos[mód]
                símismo[mód] = ParámsExperMód(mód, símismo.sim[mód], datos=datos, n_reps=símismo.n_reps)


class ParámInic(ParámCoso):

    def __init__(símismo, nombre, unids, líms, apriori):
        atribs = {'nombre': nombre, 'unids': unids, 'líms': líms, 'apriori': apriori}
        super().__init__(cls_pariente=type(nombre, (Parám,), atribs), coso=None)
