no_informativo = '0'
from .ecuaciones import ÁrbolEcs

class Calibs(object):
    def __init__(símismo, árbol_ecs):
        símismo.árbol = árbol_ecs
        símismo.ecs = símismo._árbol_a_dic(árbol_ecs)

    def espec_apriori(símismo, categ, sub_categ, ec, parám, rango, certidumbre, índs=None):
        pass

    @staticmethod
    def _árbol_a_dic(árbol):
        """

        Parameters
        ----------
        árbol ÁrbolEcs

        Returns
        -------

        """
        dic = {}
        for categ in árbol.categs:
            d_c = dic[str(árbol)] = {}
            for sub in categ.subcategs:
                d_s = d_c[str(sub)] = {}
                for ec in sub.ecs:
                    d_e = d_s[str(ec)] = {}
                    for prm in ec.paráms:
                        prm_calib = CalibParám(inter=prm.inter)
                        prm_calib

                        d_e[prm] = prm_calib
                        {
                            no_informativo: str(prm.líms)
                        }
        return dic

    def leer(símismo, arch):
        pass

    def escribir(símismo, arch):
        pass


class ÁrbolCalib(object):
    pass


class CategEcCalib(object):
    pass

class SubCategEcCalib(object):
    pass

class EcCalib(object):
    pass


class CalibParám(object):
    def __init__(símismo, inter=False):
        símismo.inter = inter
        símismo.calibs = {}


