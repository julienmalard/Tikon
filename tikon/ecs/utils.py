from tikon.ecs.dists.utils import proc_líms


def líms_compat(líms, ref):
    líms = proc_líms(líms)
    ref = proc_líms(ref)

    if not (líms[0] >= ref[0] and líms[1] <= ref[1]):
        raise ValueError('Límites {líms} incompatibles con límites teoréticos {ref}.'.format(líms=líms, ref=ref))
