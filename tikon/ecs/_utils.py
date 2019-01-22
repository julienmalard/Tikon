import numpy as np

inf = np.inf


def proc_líms(líms):
    return -inf if líms[0] is None else líms[0], inf if líms[1] is None else líms[1]


def líms_compat(líms, ref):
    líms = proc_líms(líms)
    ref = proc_líms(ref)

    if not (líms[0] >= ref[0] and líms[1] <= ref[1]):
        raise ValueError('Límites {líms} incompatibles con límites teoréticos {ref}.'.format(líms=líms, ref=ref))
