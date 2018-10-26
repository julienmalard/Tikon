from .clb_spotpy import CalibSpotPy

_opciones = [CalibSpotPy]


def gen_calibrador(método):
    try:
        return next(op for op in _opciones if método in op.métodos())
    except StopIteration:
        raise ValueError('Método de calibración "{m}" no reconocido'.format(m=método))
