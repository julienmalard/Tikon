from tikon.utils import proc_líms


def líms_compat(líms, ref):
    líms = proc_líms(líms)
    ref = proc_líms(ref)

    if not (líms[0] >= ref[0] and líms[1] <= ref[1]):
        raise ValueError('Límites {líms} incompatibles con límites teoréticos {ref}.'.format(líms=líms, ref=ref))


def calc_ajust_dist(líms, líms_dist):
    if líms[0] >= líms_dist[0]:
        if líms[1] <= líms_dist[1]:
            return {'loc': 0, 'scale': 1}
        return {'loc': 0, 'scale': 1}

    raise ValueError('Límites {líms} incompatibles con límites teoréticos {ref}.'.format(líms=líms, ref=ref))
