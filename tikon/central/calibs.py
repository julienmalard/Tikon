from copy import copy
from warnings import warn as avisar

import numpy as np
from tikon.ecs.dists import DistAnalítica, DistTraza


class EspecCalibsCorrida(object):
    def __init__(símismo, calibs=None, aprioris=False, corresp=True, heredar_inter=True):
        símismo.calibs = [calibs] if isinstance(calibs, str) else calibs
        símismo.aprioris = aprioris
        símismo.corresp = corresp
        símismo.heredar_inter = heredar_inter

    def llenar_vals(símismo, l_vals_prm, n_reps):

        sin_aprioris = list(l_vals_prm)
        if símismo.aprioris:
            for prm in l_vals_prm:
                if prm.apriori(heredar=símismo.heredar_inter):
                    prm.llenar_de_apriori(heredar=símismo.heredar_inter)
                    sin_aprioris.remove(prm)

        símismo.filtrar_dists(sin_aprioris).llenar(n_reps)

    def gen_dists_calibs(símismo, l_vals_prm, permitidas):
        l_dists = []

        sin_aprioris = list(l_vals_prm)
        if símismo.aprioris:
            for val_prm in l_vals_prm:
                try:
                    existente = next(cnx for cnx in l_dists if any(_vals_prms_iguales(vl, val_prm) for vl in cnx.vals))
                    existente.vals.append(val_prm)
                except StopIteration:
                    apriori = val_prm.apriori()
                    if apriori:
                        if apriori.nombre_dist not in permitidas:
                            raise ValueError(apriori.nombre_dist)
                        l_dists.append(ConexPrmsDist(val_prm, apriori))
                        sin_aprioris.remove(val_prm)
        símismo.filtrar_dists(sin_aprioris).llenar_lista_calibs(l_dists, permitidas=permitidas)
        return l_dists

    def filtrar_dists(símismo, l_vals_prm):
        dists_disp = [pr.dists_disp(símismo.heredar_inter) for pr in l_vals_prm]

        if símismo.calibs is not None:
            for i, prm in enumerate(dists_disp):
                dists_disp[i] = {nmb: dist for nmb, dist in prm.items() if nmb in símismo.calibs}

        if símismo.corresp:
            comunes = [
                dist for dist in set(d for prm in dists_disp for d in prm) if all(dist in prm for prm in dists_disp)
            ]
            if comunes:
                dists_disp = [{nmb: dist for nmb, dist in prm.items() if nmb in comunes} for prm in dists_disp]
            elif any(len(d) for d in dists_disp):
                avisar('No se pudo guardar correspondencia entre calibraciones.')

        return DistsFiltradas(l_vals_prm, dists_disp)


def _gen_espec_calibs(calibs, aprioris, heredar, corresp):
    if isinstance(calibs, EspecCalibsCorrida):
        return calibs
    else:
        return EspecCalibsCorrida(calibs, aprioris=aprioris, corresp=corresp, heredar_inter=heredar)


class ConexPrmsDist(object):
    def __init__(símismo, val_prm, dist):
        símismo.dist = copy(dist)
        símismo.vals = [val_prm]

    def aplicar_val(símismo, val):
        for v in símismo.vals:
            v.val = símismo.dist.transf_vals(val)

    def guardar_traza(símismo, nombre, vals, pesos):
        dist = DistTraza(trz=símismo.dist.transf_vals(vals), pesos=pesos)
        símismo.vals[0].guardar_calibs(dist, nombre=nombre)


class DistsFiltradas(object):
    def __init__(símismo, l_vals_prms, dists_disp, permitidas=None):
        símismo.vals_prms = l_vals_prms
        símismo.dists_disp = dists_disp
        símismo.permitidas = permitidas

    def llenar(símismo, n_reps):

        índs_dists = {}
        for prm, d_dists in zip(símismo.vals_prms, símismo.dists_disp):
            n_dists = len(d_dists)
            if n_dists == 0:
                prm.llenar_de_base()
            else:
                n_por_dist = np.full(n_dists, n_reps // n_dists)
                extras = n_reps % n_dists
                n_por_dist[:extras] += 1

                # Intentar preservar correspondencias como posible aunque `corresp` sea ``Falso``
                for í, (nmb, dist) in enumerate(d_dists.items()):
                    tmñ = dist.tmñ()
                    if nmb not in índs_dists:
                        índs_dists[nmb] = {tmñ: np.random.randint(tmñ, size=n_por_dist[í])}
                    elif tmñ not in índs_dists:
                        índs_dists[nmb][tmñ] = np.random.randint(tmñ, size=n_por_dist[í])
                prm.llenar_de_dists([(d_dists[nmb], índs_dists[nmb][tmñ]) for nmb in d_dists])

    def llenar_lista_calibs(símismo, lista, permitidas):

        for val_prm, d_dists in zip(símismo.vals_prms, símismo.dists_disp):
            try:
                existente = next(cnx for cnx in lista if any(_vals_prms_iguales(vl, val_prm) for vl in cnx.vals))
                existente.vals.append(val_prm)
                continue
            except StopIteration:
                pass
            l_dists = list(d_dists.values())
            n_dists = len(d_dists)

            if n_dists == 0:
                dist_base = val_prm.dist_base()
                if dist_base.nombre_dist not in permitidas:
                    raise ValueError('Distribución de base {nmbr} no permitida.'.format(nmbr=dist_base.nombre_dist))
                lista.append(ConexPrmsDist(val_prm, dist=dist_base))

            elif n_dists == 1 and (isinstance(l_dists[0], DistAnalítica) and l_dists[0].nombre_dist in permitidas):
                lista.append(ConexPrmsDist(val_prm, dist=l_dists[0]))
            else:
                traza = np.ravel((d.obt_vals(100) for d in d_dists.values()))
                lista.append(
                    ConexPrmsDist(val_prm, dist=DistAnalítica.de_traza(traza, líms=val_prm.líms, permitidas=permitidas))
                )


def _vals_prms_iguales(v1, v2):
    return (v1.prm is v2.prm) and (v1.inter == v2.inter)
