from .sens_salib import SensSALib

_opciones = [SensSALib]


def gen_anlzdr_sensib(método, paráms, calibs):
    try:
        cls = next(op for op in _opciones if método in op.métodos)
    except StopIteration:
        raise ValueError('Método de análisis de sensibilidad "{m}" no reconocido.'.format(m=método))

    return cls(método=método, paráms=paráms, calibs=calibs)
