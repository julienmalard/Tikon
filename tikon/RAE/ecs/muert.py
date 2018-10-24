import numpy as np

from tikon.calibs import CategEc, SubCategEc, Ecuación, Parám

inf = np.inf

ecs_muert = CategEc(
    'Muertes',
    subs=[
        SubCategEc(
            'Ecuación',
            ecs=[
                Ecuación('Nada'),
                Ecuación(
                    'Constante',
                    paráms=[
                        Parám('q', (0, 1))
                    ]
                ),
                Ecuación(
                    'Log Normal Temperatura',
                    paráms=[
                        Parám('t', (-inf, inf)),
                        Parám('p', (0, inf))
                    ]
                ),
                Ecuación(
                    'Asimptótico Humedad',
                    paráms=[
                        Parám('a', (0, inf)),
                        Parám('b', (-inf, inf))
                    ]
                ),
                Ecuación(
                    'Sigmoidal Temperatura',
                    paráms=[
                        Parám('a', (-inf, inf)),
                        Parám('b', (0, inf))
                    ]
                )
            ]
        )
    ]
)
