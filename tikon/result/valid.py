from tikon.result.proc import ens, n_existen, prom_vals, suma_pesos, Procesador


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


class ValidÍnds(PlantillaValid):
    pass


class ValidRes(PlantillaValid):
    def __init__(símismo, valids, proc):
        símismo.valids = valids
        criterios = {
            cr: proc.combin(vals=[v[cr] for v in valids], pesos=[v.peso for v in valids]) if valids else None
            for cr in proc.criterios
        }
        peso = proc.combin_pesos([v.peso for v in valids]) if valids else 0
        super().__init__(criterios, peso)


class Valid(PlantillaValid):
    def __init__(símismo, ramas, proc):
        criterios = {
            cr: proc.combin(
                vals=[v[cr] for v in ramas.values() if v.peso], pesos=[v.peso for v in ramas.values() if v.peso]
            ) for cr in proc.criterios
        }
        peso = proc.combin_pesos([v.peso for v in ramas.values()])
        símismo.ramas = ramas

        super().__init__(criterios, peso)

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
            lambda o, s: {ll: v(o, s) for ll, v in f_vals.items()},
            f_pesos, f_combin, f_combin_pesos
        )
