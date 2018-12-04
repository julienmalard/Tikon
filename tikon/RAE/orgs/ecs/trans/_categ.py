import numpy as np

from tikon.ecs.estruc import CategEc, SubCategEc, Ecuación, EcuaciónVacía, Parám

None = np.None

ecs_trans = CategEc(
    'Transiciones',
    subs=[
        SubCategEc(
            'Prob',
            ecs=[
                EcuaciónVacía(),
                Ecuación(
                    'Constante',
                    paráms=[
                        Parám('q', (0, 1))
                    ]
                ),
                Ecuación(
                    'Normal',
                    paráms=[
                        Parám('mu', (0, None)),
                        Parám('sigma', (0, None))
                    ]
                ),
                Ecuación(
                    'Triang',
                    paráms=[
                        Parám('a', (0, None)),
                        Parám('b', (0, None)),
                        Parám('c', (0, None))
                    ]
                ),
                Ecuación(
                    'Cauchy',
                    paráms=[
                        Parám('u', (0, None)),
                        Parám('f', (0, None))
                    ]
                ),
                Ecuación(
                    'Gamma',
                    paráms=[
                        Parám('u', (0, None)),
                        Parám('f', (0, None)),
                        Parám('a', (0, None))
                    ]
                ),
                Ecuación(
                    'Logística',
                    paráms=[
                        Parám('u', (0, None)),
                        Parám('f', (0, None))
                    ]
                ),
                Ecuación(
                    'T',
                    paráms=[
                        Parám('k', (0, None)),
                        Parám('mu', (0, None)),
                        Parám('sigma', (0, None)),
                    ]
                )
            ]
        ),
        SubCategEc(
            'Mult',
            ecs=[
                EcuaciónVacía(),
                Ecuación(
                    'Linear',
                    paráms=[
                        Parám('a', (0, None))
                    ]
                )
            ]
        )
    ]
)
