import matplotlib.pyplot as dib
import numpy as np
import pymc
from Matemáticas.Incert import trazas_a_dists

i = 0
adaptivo = True
emp = 0
fin = 60
print(emp, fin)
n_iter = 1000


class ModBayes(object):
    def __init__(símismo, función, dic_argums, d_obs, lista_d_paráms, aprioris, lista_líms, id_calib,
                 función_llenar_coefs):

        símismo.id = id_calib

        l_var_paráms = trazas_a_dists(id_simul=símismo.id, l_d_pm=lista_d_paráms, l_lms=lista_líms,
                                      l_trazas=aprioris, formato='calib', comunes=False)

        # Quitar variables sin incertidumbre. Por una razón muy rara, simul() no funcionará en PyMC sino. # Quitar variables sin incertidumbre. Sino, por una razón muy rara, simul() no funcionará en PyMC.
        l_var_paráms_final = []
        for v in l_var_paráms:
            vrs = v.obt_var()
            if isinstance(vrs, list):
                l_var_paráms_final.extend(vrs)
            else:
                l_var_paráms_final.append(vrs)


        # Llenamos las matrices de coeficientes con los variables PyMC recién creados.
        función_llenar_coefs(nombre_simul=id_calib, n_rep_parám=1, dib_dists=False)

        def fun(**kwargs):
            global i
            print(i)
            i += 1

            res = función(**kwargs)['Normal']

            return res

        @pymc.deterministic(trace=True)
        def simul(_=l_var_paráms):
            return fun(**dic_argums)

        l_var_obs = []

        for tipo, obs in d_obs.items():
            if tipo == 'Normal':
                tau = 1 / simul['sigma'] ** 2
                var_obs = pymc.Normal('obs', mu=simul['mu'], tau=tau, value=obs, observed=True)
                l_var_obs.extend([var_obs, tau])

        símismo.MCMC = pymc.MCMC({simul, *l_var_paráms, *l_var_obs})

    def calib(símismo, rep, quema, extraer, **kwargs):

        if adaptivo:
            símismo.MCMC.use_step_method(pymc.AdaptiveMetropolis, símismo.MCMC.stochastics)

        símismo.MCMC.sample(iter=rep, burn=quema, thin=extraer, verbose=1)

        for v in símismo.MCMC.variables:
            if False:
                try:
                    dib.plot(símismo.MCMC.trace(v.__name__)[:])
                    dib.title(v.__name__)
                    dib.show()
                except (TypeError, KeyError):
                    pass
            try:
                print('{}\n\t'.format(v.__name__), símismo.MCMC.trace(v.__name__)[:])
                print('************')
            except (TypeError, KeyError):
                pass


líms = [[0.006143547954646662, 0.004143547954646662], [0.02641613017892241, 0.02561613017892241], [3.6560851733914808, 3.2560851733914804], [1.9650416697683102, 1.36504166976831], [1.0043484484635446e-08, 8.905226359823514e-09], [5.2344154421948645e-17, 3.584930542917252e-17], [0.01, 0.008424049215276837], [0.05278370675938784, 0.034783706759387835], [8.344156186512684, 7.544156186512684], [1.859969480435551, 1.259969480435551], [8.408452689594336e-09, 7.270194564782404e-09], [7.937490983672413e-17, 6.288006084394801e-17], [0.009822133533670865, 0.007822133533670866], [0.02360183840006633, 0.012018505066732996], [6.735045441220312, 6.335045441220312], [2.935368687970388, 2.3353686879703885], [6.767427175972795e-09, 5.629169051160862e-09], [3.5942494909704755e-17, 1.9447645916928642e-17], [0.0010892446260036938, 0.0], [0.06456888904570236, 0.052985555712369035], [7.993218921346308, 7.593218921346308], [3.805551951662424, 3.2055519516624242], [9.473954656090874e-09, 8.335696531278942e-09], [6.156900521985185e-17, 4.507415622707573e-17], [0.0017283406835598317, 0.0], [0.125, 0.1132149097879174], [6.0, 5.630711932400921], [2.6814139049624686, 2.081413904962469], [5.2171445961448266e-09, 4.4000086539813725e-09], [8.532503690773825e-17, 6.883018791496213e-17], [0.005909086460391245, 0.003909086460391245], [0.08149692925899343, 0.06499187875394291], [11.0, 10.70688092264144], [1.4300829767935785, 1.0], [0.0067909413050695555, 0.0047909413050695555], [0.024449742955003222, 0.008862441367701635], [7.81351465785079, 7.41351465785079], [3.9871155195555192, 3.3871155195555196], [0.0041580911542028875, 0.002158091154202888], [3.408383637925069, 3.0083836379250686], [92.78184230132567, 73.48184230132566], [1.667745375005944, 1.467745375005944], [7.454915463070574, 6.2949154630705735], [3.1526724082578497, 2.55267240825785], [0.0076823064053704575, 0.0056823064053704575], [9.866900929997412, 8.066900929997411], [10.061451653132691, 9.661451653132692], [0.6, 0.5839890199595302], [1.3450794438657239, 1.0950794438657239], [0.7643829171197258, 0.5143829171197258], [0.48207860410886627, 0.25], [290743531.36023504, 110743531.36023504], [279281018.73310006, 100000000.0], [585476626.0580845, 405476626.0580845], [0.006723886177260551, 0.004723886177260551], [18.586660304562358, 16.586660304562358], [8.043619184444477, 7.043619184444478], [0.003894993948127248, 0.001894993948127248], [5.186734565996787, 3.3867345659967865], [7.994937321302886, 7.5949373213028855], [0.589093500637263, 0.5690935006372629], [0.8656415159401634, 0.6156415159401634], [490321.97721997125, 100000.0], [0.01, 0.008765390303566392], [14.580562059315994, 12.580562059315994], [8.428071586548748, 7.428071586548748], [0.1, 0.0]]

if __name__ == '__main__':

    fac = 1e8
    datos = np.random.normal(5*fac, 1*fac, 50)
    print('Datos', datos)
    print('******************')

    if False:
        for l in líms:
            i = 0
            print(l)

            dic_paráms = {'sigma': None, 'mu': None}

            def fun0():
                s = np.zeros(5)
                m = np.zeros(5)
                s[:] = dic_paráms['sigma']
                m[:] = dic_paráms['mu']

                return {'Normal': {'sigma': s, 'mu': m}}

            def f(**kwargs):
                for i, ll in enumerate(sorted(dic_paráms)):
                    dic_paráms[ll] = l_d_paráms[i]['prueba']

            d_args = {}

            d_obs = {'Normal': datos}

            l_d_paráms = [{'a': 'Uniforme~({}, {})'.format(l[0], l[1])}, {'a': 'Gamma~(1, 0, 1)'}]

            l_líms = [(-np.inf, np.inf), (0, np.inf)]

            m = ModBayes(función=fun0, dic_argums=d_args, d_obs=d_obs, lista_d_paráms=l_d_paráms ,
                         aprioris=[['a'], ['a']], lista_líms=l_líms, id_calib='prueba', función_llenar_coefs=f)
            m.calib(rep=n_iter, quema=0, extraer=1)

    else:
        # Prueba estúpidamente sencilla (porque las otras pruebas no funcionan...)
        var_mu = pymc.Uniform('mu', 0, 10)
        var_s = pymc.Gamma('sigma', 1, 10)
        var_mu_trans = var_mu * fac
        var_s_trans = var_s * fac
        var_0 = pymc.Uniform('0', 0, 10)
        l = [pymc.Normal('z_{}'.format(i), 1, 2) for i in range(100)]

        @pymc.deterministic()
        def func_todo(mu=var_mu_trans, s=var_s_trans, _=l):
            a = [x / 10000 for x in _]
            return {'mu': mu}

        obs = pymc.Normal('obs', mu=func_todo['mu'], tau=1 / var_s_trans ** 2, value=datos, trace=True, observed=True)
        mod_prueba = pymc.MCMC((var_mu, var_s, func_todo, var_mu_trans, var_s_trans, obs, var_0, *l))
        if adaptivo:
            mod_prueba.use_step_method(pymc.AdaptiveMetropolis, mod_prueba.stochastics)
        mod_prueba.sample(iter=n_iter, burn=0, thin=1, verbose=0)

        for v in mod_prueba.variables:
            if v.__name__[0] != 'z':
                try:
                    dib.plot(mod_prueba.trace(v.__name__)[:])
                    dib.title(v.__name__)
                    dib.show()
                except (TypeError, KeyError):
                    pass
                try:
                    print('{}\n\t'.format(v.__name__), mod_prueba.trace(v.__name__)[:])
                    print('************')
                except (TypeError, KeyError):
                    pass
