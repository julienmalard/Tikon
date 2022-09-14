from typing import Union

import numpy as np
import numpy.typing as npty

Tipo_Valor_Numérico = Union[int, float, np.number]
Tipo_Valor_Numérico_Entero = Union[int, np.integer]

Tipo_Matriz_Numérica = npty.NDArray[np.number]
Tipo_Matriz_Núm_Entero = npty.NDArray[np.integer]
