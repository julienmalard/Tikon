import unittest
from warnings import warn as avisar

import scipy.stats as estad
from pruebas.test_central.rcrs.modelo_calib import generar
from tikon.calibrador.spotpy_ import EMV, RS, BDD, CMEDZ, MC, MLH, CAACAA, CAA, ECBUA, ERP, CMMC, CalibSpotPy
from tikon.ecs.aprioris import APrioriDist


class PruebaSpotPy(unittest.TestCase):
    def test_algs(símismo):
        for alg in [EMV, RS, BDD, CMEDZ, MC, MLH, CAACAA, CAA, ECBUA, ERP, CMMC]:
            with símismo.subTest(alg.__name__):
                gen = generar()
                modelo = gen['modelo']
                exper = gen['exper']
                modelo.calibrar('calib', exper, calibrador=alg(), n_iter=30)
                valid = modelo.simular('valid', exper, calibs=['calib']).validar()
                if valid['ens'] < 0.90:
                    avisar('Algoritmo {alg} no funciona muy bien.'.format(alg=alg.__name__))

    def test_dists(símismo):
        dists_aprioris = {
            'Normal': estad.norm(1, 2),
            'Uniforme': estad.uniform(0, 3),
            'LogNormal': estad.lognorm(1, 0, 2),
            'Chi2': estad.chi2(1, 0, 2),
            'Exponencial': estad.expon(0, 2),
            'Gamma': estad.gamma(1, 0, 1),
            'Triang': estad.triang(0.5, 0, 2)
        }
        for nombre in CalibSpotPy.dists_disp:
            dist = dists_aprioris[nombre]
            with símismo.subTest(nombre):
                gen = generar()
                modelo = gen['modelo']
                exper = gen['exper']
                coso = gen['coso']
                apr = APrioriDist(dist)

                coso.espec_apriori(apr, categ='categ', sub_categ='subcateg', ec='ec', prm='a')
                modelo.calibrar('calib', exper, n_iter=30)

                coso.borrar_aprioris()
                valid = modelo.simular('valid', exper, calibs=['calib']).validar()
                símismo.assertGreater(valid['ens'], 0.95)
