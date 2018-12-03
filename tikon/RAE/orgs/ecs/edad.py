import numpy as np

from tikon.ecs.estruc import CategEc, SubCategEc, Ecuación, EcuaciónVacía, Parám

inf = np.inf

ecs_edad = CategEc(
    'Edad',
    subs=[
        SubCategEc(
            'Ecuación',
            ecs=[
                EcuaciónVacía(),
                Ecuación('Días'),  # No se necesitan coeficientes en este caso
                Ecuación(
                    'Días grados',
                    paráms=[
                        Parám('mín', (-inf, inf)),
                        Parám('máx', (-inf, inf))
                    ]
                ),
                Ecuación(
                    'Brière Temperatura',
                    paráms=[
                        Parám('t_dev_mín', (-inf, inf)),
                        Parám('t_letal', (-inf, inf))
                    ]
                ),
                Ecuación(
                    'Logan Temperatura',
                    paráms=[
                        Parám('rho', (0, 1)),
                        Parám('delta', (0, 1)),
                        Parám('t_letal', (-inf, inf))
                    ]
                ),
                Ecuación(
                    'Brière No Linear Temperatura',
                    paráms=[
                        Parám('t_dev_mín', (-inf, inf)),
                        Parám('t_letal', (-inf, inf)),
                        Parám('m', (0, inf))
                    ]
                )
            ]
        )
    ]
)
