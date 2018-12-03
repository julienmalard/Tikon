import numpy as np

from tikon.ecs.estruc import CategEc, SubCategEc, Ecuación, EcuaciónVacía, Parám

inf = np.inf

ecs_repr = CategEc(
    'Reproducción',
    subs=[
        SubCategEc(
            'Prob',
            ecs=[
                EcuaciónVacía(),
                Ecuación(
                    'Constante',
                    paráms=[
                        Parám('a', (0, inf))
                    ]
                ),
                Ecuación(
                    'Normal',
                    paráms=[
                        Parám('n', (0, inf)),
                        Parám('mu', (0, inf)),
                        Parám('sigma', (0, inf))
                    ]
                ),
                Ecuación(
                    'Triang',
                    paráms=[
                        Parám('n', (0, inf)),
                        Parám('a', (0, inf)),
                        Parám('b', (0, inf)),
                        Parám('c', (0, inf))
                    ]
                ),
                Ecuación(
                    'Cauchy',
                    paráms=[
                        Parám('n', (0, inf)),
                        Parám('u', (0, inf)),
                        Parám('f', (0, inf))
                    ]
                ),
                Ecuación(
                    'Gamma',
                    paráms=[
                        Parám('n', (0, inf)),
                        Parám('u', (0, inf)),
                        Parám('f', (0, inf)),
                        Parám('a', (0, inf))
                    ]
                ),
                Ecuación(
                    'Logística',
                    paráms=[
                        Parám('n', (0, inf)),
                        Parám('u', (0, inf)),
                        Parám('f', (0, inf))
                    ]
                ),
                Ecuación(
                    'T',
                    paráms=[
                        Parám('n', (0, inf)),
                        Parám('k', (0, inf)),
                        Parám('mu', (0, inf)),
                        Parám('sigma', (0, inf)),
                    ]
                )
            ]
        )
    ]
)
