import unittest

from tikon.móds.rae.red.obs import ObsPobs, ObsDepred, ObsTrans, ObsCrec, ObsEmigr, ObsImigr, ObsMov, ObsMuerte, ObsRepr


class PruebaObs(unittest.TestCase):
    @unittest.skip('implementar')
    def test_obs_pobs(símismo):
        obs = ObsPobs.de_pandas()

    @unittest.skip('implementar')
    def test_obs_depred(símismo):
        obs = ObsDepred.de_pandas()

    @unittest.skip('implementar')
    def test_obs_trans(símismo):
        obs = ObsTrans.de_pandas()

    @unittest.skip('implementar')
    def test_obs_crec(símismo):
        obs = ObsCrec.de_pandas()

    @unittest.skip('implementar')
    def test_obs_emigr(símismo):
        obs = ObsEmigr.de_pandas()

    @unittest.skip('implementar')
    def test_obs_imigr(símismo):
        obs = ObsImigr.de_pandas()

    @unittest.skip('implementar')
    def test_obs_mov(símismo):
        obs = ObsMov.de_pandas()

    @unittest.skip('implementar')
    def test_obs_muerte(símismo):
        obs = ObsMuerte.de_pandas()

    @unittest.skip('implementar')
    def test_obs_repr(símismo):
        obs = ObsRepr.de_pandas()
