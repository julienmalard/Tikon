import unittest

from tikon.datos import proc

from .rcrs.modelo_valid import modelo, exper


class PruebaValid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = modelo.simular('valid', exper)

    def test_valid(símismo):
        valid = símismo.res.validar()
        símismo.assertDictEqual(valid.criterios, {'ens': 1.0})

    def test_criterios(símismo):
        crits = [
            proc.r2, proc.rcep, proc.rcnep, proc.corresp, proc.ekg, proc.log_p,
            proc.r2_percentiles, proc.rcnep_percentiles
        ]
        valids = símismo.res.validar(proc=crits)
        símismo.assertSetEqual(set(valids.criterios), {cr.__name__ for cr in crits})

    def test_nombres_criterios(símismo):
        crits = {'R cuadrado': proc.r2, 'otro nombre': proc.rcep}
        valids = símismo.res.validar(proc=crits)
        símismo.assertSetEqual(set(valids.criterios), set(crits))
