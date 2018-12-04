import numpy as np

from tikon.ecs.estruc import CategEc, SubCategEc, Ecuación, Parám, FuncEc


class Normal(FuncEc):
    """
    Error distribuido de manera normal.
    """
    def __call__(self, cf, paso, mnjdr_móds):
        return cf['sigma'] * paso


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
                    ],
                    fun=Normal
                )
            ]
        )
    ]
)
