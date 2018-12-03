import numpy as np

from tikon.ecs.estruc import CategEc, SubCategEc, Ecuación, Parám

inf = np.inf

ecs_estoc = CategEc(
    'Estoc',
    subs=[
        SubCategEc(
            'Dist',
            ecs=[
                Ecuación(
                    'Normal',
                    paráms=[
                        Parám('sigma', (0, 1))
                    ]
                )
            ]
        )
    ]
)
