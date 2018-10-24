import numpy as np

from tikon.calibs import CategEc, SubCategEc, Ecuación, Parám

inf = np.inf

ecs_trans = CategEc(
    'Transiciones',
    subs=[
        SubCategEc(
            'Prob',
            ecs=[
                Ecuación('Nada'),
                Ecuación(
                    'Constante',
                    paráms=[
                        Parám('q', (0, 1))
                    ]
                ),
                Ecuación(
                    'Normal',
                    paráms=[
                        Parám('mu', (0, inf)),
                        Parám('sigma', (0, inf))
                    ]
                ),
                Ecuación(
                    'Triang',
                    paráms=[
                        Parám('a', (0, inf)),
                        Parám('b', (0, inf)),
                        Parám('c', (0, inf))
                    ]
                ),
                Ecuación(
                    'Cauchy',
                    paráms=[
                        Parám('u', (0, inf)),
                        Parám('f', (0, inf))
                    ]
                ),
                Ecuación(
                    'Gamma',
                    paráms=[
                        Parám('u', (0, inf)),
                        Parám('f', (0, inf)),
                        Parám('a', (0, inf))
                    ]
                ),
                Ecuación(
                    'Logística',
                    paráms=[
                        Parám('u', (0, inf)),
                        Parám('f', (0, inf))
                    ]
                ),
                Ecuación(
                    'T',
                    paráms=[
                        Parám('k', (0, inf)),
                        Parám('mu', (0, inf)),
                        Parám('sigma', (0, inf)),
                    ]
                )
            ]
        ),
        SubCategEc(
            'Mult',
            ecs=[
                Ecuación('Nada'),
                Ecuación(
                    'Linear',
                    paráms=[
                        Parám('a', (0, inf))
                    ]
                )
            ]
        )
    ]
)
