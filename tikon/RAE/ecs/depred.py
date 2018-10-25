import numpy as np

from tikon.calibs import CategEc, SubCategEc, Ecuación, Parám

inf = np.inf

ecs_depred = CategEc(
    'Depredación',
    subs=[
        SubCategEc(
            'Ecuación',
            ecs=[
                Ecuación('Nada'),
                Ecuación(
                    'Tipo I_Dependiente presa',
                    paráms=[
                        Parám('a', (0, 1), inter=['presa', 'huésped'])
                    ]
                ),
                Ecuación(
                    'Tipo II_Dependiente presa',
                    paráms=[
                        Parám('a', (0, 1), inter=['presa', 'huésped']),
                        Parám('b', (0, inf), inter=['presa', 'huésped'])
                    ]
                ),
                Ecuación(
                    'Tipo III_Dependiente presa',
                    paráms=[
                        Parám('a', (0, 1), inter=['presa', 'huésped']),
                        Parám('b', (0, inf), inter=['presa', 'huésped'])
                    ]
                ),
                Ecuación(
                    'Tipo I_Dependiente ratio',
                    paráms=[
                        Parám('a', (0, 1), inter=['presa', 'huésped'])
                    ]
                ),
                Ecuación(
                    'Tipo II_Dependiente ratio',
                    paráms=[
                        Parám('a', (0, 1), inter=['presa', 'huésped']),
                        Parám('b', (0, inf), inter=['presa', 'huésped'])
                    ]
                ),
                Ecuación(
                    'Tipo III_Dependiente ratio',
                    paráms=[
                        Parám('a', (0, 1), inter=['presa', 'huésped']),
                        Parám('b', (0, inf), inter=['presa', 'huésped'])
                    ]
                ),
                Ecuación(
                    'Beddington-DeAngelis',
                    paráms=[
                        Parám('a', (0, 1), inter=['presa', 'huésped']),
                        Parám('b', (0, inf), inter=['presa', 'huésped']),
                        Parám('c', (0, inf), inter=['presa', 'huésped'])
                    ]
                ),
                Ecuación(
                    'Tipo I_Hassell-Varley',
                    paráms=[
                        Parám('a', (0, inf), inter=['presa', 'huésped']),
                        Parám('m', (0, inf), inter=['presa', 'huésped']),
                    ]
                ),
                Ecuación(
                    'Tipo II_Hassell-Varley',
                    paráms=[
                        Parám('a', (0, inf), inter=['presa', 'huésped']),
                        Parám('b', (0, inf), inter=['presa', 'huésped']),
                        Parám('m', (0, inf), inter=['presa', 'huésped'])
                    ]
                ),
                Ecuación(
                    'Tipo III_Hassell-Varley',
                    paráms=[
                        Parám('a', (0, inf), inter=['presa', 'huésped']),
                        Parám('b', (0, inf), inter=['presa', 'huésped']),
                        Parám('m', (0, inf), inter=['presa', 'huésped'])
                    ]
                ),
                Ecuación(
                    'Kovai',
                    paráms=[
                        Parám('a', (0, inf), inter=['presa', 'huésped']),
                        Parám('b', (0, inf), inter=['presa', 'huésped'])
                    ]
                )
            ],
            activa='Kovai'
        )
    ]
)
