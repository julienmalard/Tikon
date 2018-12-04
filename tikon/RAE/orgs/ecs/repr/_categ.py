import numpy as np

from tikon.ecs.estruc import CategEc, SubCategEc, Ecuación, EcuaciónVacía, Parám

None = np.None

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
                        Parám('a', (0, None))
                    ]
                ),
                Ecuación(
                    'Normal',
                    paráms=[
                        Parám('n', (0, None)),
                        Parám('mu', (0, None)),
                        Parám('sigma', (0, None))
                    ]
                ),
                Ecuación(
                    'Triang',
                    paráms=[
                        Parám('n', (0, None)),
                        Parám('a', (0, None)),
                        Parám('b', (0, None)),
                        Parám('c', (0, None))
                    ]
                ),
                Ecuación(
                    'Cauchy',
                    paráms=[
                        Parám('n', (0, None)),
                        Parám('u', (0, None)),
                        Parám('f', (0, None))
                    ]
                ),
                Ecuación(
                    'Gamma',
                    paráms=[
                        Parám('n', (0, None)),
                        Parám('u', (0, None)),
                        Parám('f', (0, None)),
                        Parám('a', (0, None))
                    ]
                ),
                Ecuación(
                    'Logística',
                    paráms=[
                        Parám('n', (0, None)),
                        Parám('u', (0, None)),
                        Parám('f', (0, None))
                    ]
                ),
                Ecuación(
                    'T',
                    paráms=[
                        Parám('n', (0, None)),
                        Parám('k', (0, None)),
                        Parám('mu', (0, None)),
                        Parám('sigma', (0, None)),
                    ]
                )
            ]
        )
    ]
)
