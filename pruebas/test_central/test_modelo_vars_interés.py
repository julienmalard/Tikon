import unittest

from .rcrs.vars_interés import modelo, exper, exper_obs_1_1


class PruebaVarsInterés(unittest.TestCase):

    def _verif_incluido(símismo, l_vars, res):
        for var in l_vars:
            mód, var = var.split('.')
            with símismo.subTest(mód=mód, var=var):
                símismo.assertIsNotNone(res['exper'][mód][var].t)

    def _verif_excluido(símismo, l_vars, res):
        for var in l_vars:
            mód, var = var.split('.')
            with símismo.subTest(mód=mód, var=var):
                símismo.assertIsNone(res['exper'][mód][var].t)

    def test_todos(símismo):
        res = modelo.simular('todos', exper, t=2, vars_interés=True)
        símismo._verif_incluido(['módulo 1.res 1_1', 'módulo 1.res 1_2', 'módulo 2.res 2_1', 'módulo 2.res 2_2'], res)

    def test_ninguno(símismo):
        res = modelo.simular('todos', exper, t=2, vars_interés=False)
        símismo._verif_excluido(['módulo 1.res 1_1', 'módulo 1.res 1_2', 'módulo 2.res 2_1', 'módulo 2.res 2_2'], res)

    def test_obs(símismo):
        res = modelo.simular('todos', exper_obs_1_1, t=2)
        símismo._verif_incluido(['módulo 1.res 1_1'], res)
        símismo._verif_excluido(['módulo 1.res 1_2', 'módulo 2.res 2_1', 'módulo 2.res 2_2'], res)

    def test_nombres(símismo):
        res = modelo.simular('todos', exper, t=2, vars_interés=['módulo 2.res 2_2'])
        símismo._verif_incluido(['módulo 2.res 2_2'], res)
        símismo._verif_excluido(['módulo 1.res 1_1', 'módulo 1.res 1_2', 'módulo 2.res 2_1'], res)

    def test_módulos(símismo):
        res = modelo.simular('todos', exper, t=2, vars_interés=['módulo 1'])
        símismo._verif_incluido(['módulo 1.res 1_1', 'módulo 1.res 1_2'], res)
        símismo._verif_excluido(['módulo 2.res 2_1', 'módulo 2.res 2_2'], res)

    def test_mixto(símismo):
        res = modelo.simular('todos', exper, t=2, vars_interés=['módulo 2', 'módulo 1.res 1_1'])

        símismo._verif_incluido(['módulo 1.res 1_1', 'módulo 2.res 2_1', 'módulo 2.res 2_2'], res)
        símismo._verif_excluido(['módulo 1.res 1_2'], res)
