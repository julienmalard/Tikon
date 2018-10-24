from warnings import warn as avisar

import numpy as np
import pymc3 as pm3
import theano.tensor as tt
from theano.compile.ops import as_op

"""
Código únicamente para pruebas de algoritmos y variables de calibración bayesiana con PyMC.
"""

adaptivo = None
n_iter = 10000

if __name__ == '__main__':

    fac = 1e8
    datos = np.random.normal(5 * fac, 1 * fac, 50)
    print('Datos', datos)
    print('******************')

    if True:
        # Prueba estúpidamente sencilla (porque las otras pruebas no funcionan...)
        mod = pm3.Model()

        with mod:
            var_mu = pm3.Uniform(name='mu', lower=0, upper=10)
            var_s = pm3.Gamma(name='sigma', alpha=1, beta=10)
            var_mu_trans = var_mu * fac
            var_s_trans = var_s * fac
            var_0 = pm3.Uniform(name='0', lower=0, upper=10)
            l = [pm3.Uniform(name='z_{}'.format(i), lower=1, upper=2) for i in range(100)]


            @as_op(itypes=[tt.dscalar, tt.dscalar, tt.dscalar], otypes=[tt.dscalar, tt.dscalar])
            def func_todo(mu=var_mu_trans, s=var_s_trans, _=l):
                a = [x / 10000 for x in _]
                return mu, s


            obs = pm3.Normal(name='obs', mu=func_todo[0], sd=func_todo[1], observed=datos)

            if adaptivo:
                avisar('Método de paso establecido automáticamente.')

            t = pm3.sample(draws=n_iter)
    else:
        from Matemáticas.Variables import VarPyMC3

        var_mu = VarPyMC3('mu', 'Uniforme', {'ubic': 0, 'escl': 10 * fac})
        var_s = VarPyMC3('sigma', 'Gamma', {'a': 1, 'ubic': 0, 'escl': 10 * fac})
        var_0 = VarPyMC3('0', 'Uniforme', {'ubic': 0, 'escl': 10})
        l_0 = [VarPyMC3('z_{}'.format(i), 'Normal', {'ubic': 1, 'escl': 2}) for i in range(100)]
        l_vars = [v.var for v in l_0]

        # Unas pruebitas de variables generados a base de densidad y de límites. No afectan el modelo prueba aquí.
        l_pruebas_extr = [
            # VarPyMC2.de_densidad(nombre='prueba_uni', dens=0.8, líms_dens=(-3, 4), líms=(-5, 5), cont=True),
            # VarPyMC2.de_densidad(nombre='prueba_uni2', dens=1, líms_dens=(-3, 4), líms=(-5, 5), cont=True),
            #
            # VarPyMC2.de_densidad(nombre='prueba_gamma', dens=0.8, líms_dens=(-3, 4), líms=(-5, np.inf), cont=True),
            # VarPyMC2.de_densidad(nombre='prueba_gamma2', dens=1, líms_dens=(-3, 4), líms=(-5, np.inf), cont=True),
            #
            # VarPyMC2.de_densidad(nombre='prueba_norm', dens=0.8, líms_dens=(-3, 4), líms=(None, None), cont=True),
            # VarPyMC2.de_densidad(nombre='prueba_norm2', dens=1, líms_dens=(-3, 4), líms=(None, None), cont=True)
        ]


        @as_op(itypes=[tt.dscalar, tt.dscalar, tt.dscalar], otypes=[tt.dscalar, tt.dscalar])
        def func_todo(mu=var_mu.var, s=var_s.var, _=l_vars):
            d = {'mu': float(var_mu), 'sigma': float(var_s)}
            return d['mu'], d['sigma']


        obs = pm3.Normal(name='obs', mu=func_todo[0], sd=func_todo[1], observed=datos)

        t = pm3.sample()
        if adaptivo:
            avisar('Método de paso establecido automáticamente.')

    for v in t.varnames:
        if 'z' not in v.nombre and v.nombre != 'func_todo':
            pm3.traceplot(trace=t, varnames=v)

        try:
            print('{}\n\t'.format(v.nombre), v.traza())
            print('************')
        except (TypeError, KeyError):
            pass
