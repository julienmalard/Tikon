from tikon.datos.proc import ens, n_existen, prom_vals, suma_pesos, Procesador


def gen_proc_valid(proc):
    if isinstance(proc, ProcesadorValid):
        return proc
    return ProcesadorValid(f_vals=proc)


class PlantillaValid(object):
    def __init__(símismo, criterios, peso):
        símismo.criterios = criterios
        símismo.peso = peso

    def __getitem__(símismo, itema):
        return símismo.criterios[itema]

    def a_dic(símismo):
        return {'crits': símismo.criterios, 'peso': símismo.peso}

    def __repr__(símismo):
        return repr(símismo.a_dic())


class ValidÍnds(PlantillaValid):

    def __init__(símismo, criterios, peso, índs):
        símismo.índs = índs
        super().__init__(criterios, peso)

    def a_dic(símismo):
        return {'índices': {ll: str(v) for ll, v in símismo.índs.items()}, **super().a_dic()}


class ValidRes(PlantillaValid):
    def __init__(símismo, valids, proc):
        símismo.valids = valids
        criterios = {
            cr: proc.combin(vals=[v[cr] for v in valids], pesos=[v.peso for v in valids]).item() if valids else None
            for cr in proc.criterios
        }
        peso = proc.combin_pesos([v.peso for v in valids]).item() if valids else 0
        super().__init__(criterios, peso)

    def a_dic(símismo):
        return {'valids': [v.a_dic() for v in símismo.valids], **super().a_dic()}


class Valid(PlantillaValid):
    def __init__(símismo, ramas, proc):
        criterios = {
            cr: proc.combin(
                vals=[v[cr] for v in ramas.values() if v.peso], pesos=[v.peso for v in ramas.values() if v.peso]
            ).item() for cr in proc.criterios
        }
        peso = proc.combin_pesos([v.peso for v in ramas.values()]).item()
        símismo.ramas = ramas

        super().__init__(criterios, peso)

    def a_dic(símismo):
        return {
            **{
                str(ll): v.a_dic() for ll, v in símismo.ramas.items() if any(crt for crt in v.a_dic()['crits'].values())
            },
            **super().a_dic()
        }

    def __getitem__(símismo, itema):
        return símismo.criterios[itema]


class ProcesadorValid(Procesador):
    def __init__(símismo, f_vals=ens, f_pesos=n_existen, f_combin=prom_vals, f_combin_pesos=suma_pesos):
        if callable(f_vals):
            f_vals = [f_vals]
        if isinstance(f_vals, list):
            f_vals = {f.__name__: f for f in f_vals}

        símismo.criterios = list(f_vals)
        super().__init__(
            lambda o, s: {ll: v(o, s).item() for ll, v in f_vals.items()},
            f_pesos, f_combin, f_combin_pesos
        )
