import numpy as np

from tikon.rsltd.res import DimsCoh


class Cohortes(object):
    def __init__(símismo, etapas, n_rep_estoc, n_rep_parám, parc):
        símismo._etps = [etp for etp in etapas if etp.con_cohortes()]

        símismo._dims = DimsCoh(n_coh=10, n_estoc=n_rep_estoc, n_parám=n_rep_parám, parc=parc, etapas=etapas)

        símismo._pobs = np.zeros(símismo._dims.frm())
        símismo._edades = np.zeros(símismo._dims.frm())

    def agregar(símismo, nuevos, etapas):

        if not np.sum(nuevos):
            return

        # Limpiar edades de cohortes
        símismo._edades[símismo._pobs == 0] = 0

        # Las edades y las poblaciones actuales de las etapas que transicionan.
        edades = símismo._edades[símismo.rebanar(etapas)]
        pobs = símismo._pobs[símismo.rebanar(etapas)]

        # Los índices de los días cuyos cohortes tienen la edad mínima. Si hay más que un día (cohorte) con la
        # edad mínima, tomará el primero.
        i_cohs = np.argmin(edades, axis=símismo._dims.í_eje('coh')).ravel()

        í_parc, í_estoc, í_parám, í_etps = dic_predic['Matrices']['í_ejes_cohs']
        # Las edades de los cohortes con las edades mínimas.
        tmñ = dic_predic['Matrices']['tmñ_para_cohs']  # El tamaño de los cohortes, sin el eje de día
        eds_mín = matr_eds[i_cohs, í_parc, í_estoc, í_parám, í_etps].reshape(tmñ)

        # Las poblaciones que corresponden a estas edades mínimas.
        pobs_coresp_í = matr_pobs[i_cohs, í_parc, í_estoc, í_parám, í_etps].reshape(tmñ)

        # Dónde no hay población existente, reinicializamos la edad.
        eds_mín = np.where(pobs_coresp_í == 0, [0], eds_mín)

        # Calcular el peso de las edades existentes, según sus poblaciones existentes (para combinar con el nuevo
        # cohorte si hay que combinarla con un cohorte existente).
        peso_ed_ya = np.divide(pobs_coresp_í, np.add(nuevos, pobs_coresp_í))
        peso_ed_ya[np.isnan(peso_ed_ya)] = 0

        # Los edades promedios. Si no había necesidad de combinar cohortes, será la población del nuevo cohorte.
        eds_prom = np.add(np.multiply(eds_mín, peso_ed_ya), np.multiply(edad, np.subtract(1, peso_ed_ya)))

        # Guardar las edades actualizadas en los índices apropiados
        matr_eds[i_cohs, í_parc, í_estoc, í_parám, í_etps] = eds_prom.ravel()

        # Guardar las poblaciones actualizadas en los índices apropiados
        matr_pobs[i_cohs, í_parc, í_estoc, í_parám, í_etps] += nuevos.ravel()

    def quitar(símismo, muertes):

        if len(símismo.predics['Cohortes']):


            totales_pobs = np.sum(símismo._pobs, axis=0)
            quitar = np.floor(np.divide(muertes, totales_pobs) * símismo._pobs)
            quitar[np.isnan(quitar)] = 0

            np.subtract(símismo._pobs, quitar, out=símismo._pobs)

            muertes = np.subtract(muertes, quitar.sum(axis=0))

            cum_presente = np.cumsum(np.greater(símismo._pobs, 0), axis=0)
            quitar_2 = np.where(
                np.logical_and(np.greater(símismo._pobs, 0), np.less_equal(cum_presente, muertes)),
                1,
                0
            )

            np.subtract(símismo._pobs, quitar_2, out=símismo._pobs)

            np.add(quitar_2, quitar, out=quitar)

            # Si transiciona a otro cohorte (de otra etapa), implementarlo aquí
            if í_recip is not None:

                if í_don is None:
                    raise ValueError

                # Los índices (en la matriz de cohortes) de las etapas recipientes.
                í_recip_coh = [símismo.índices_cohortes.index(x) for x in í_recip]

                í_don_coh = [símismo.índices_cohortes.index(x) for x in í_don]

                # Para cada cohorte...
                for n_día in range(símismo._pobs.shape[0]):
                    # Las edades de las etapas que se quitaron
                    eds = símismo._edades[n_día, ...]

                    # Cambiar el orden de las etapas para los cohortes recipientes
                    nuevos = np.zeros_like(quitar[n_día])
                    nuevos[..., í_recip_coh] = quitar[n_día][..., í_don_coh]
                    símismo.agregar(nuevos, edad=eds)

    def ajustar(símismo, cambio):
        # Detectar dónde el cambio es positivo y dónde es negativo
        positivos = np.where(cambio > 0, cambio, [0])
        negativos = np.where(cambio < 0, -cambio, [0])

        # Agregar los positivos...
        símismo.agregar(positivos)

        # ...y quitar los negativos.
        símismo.quitar(negativos)

    def trans(símismo, cambio_edad, dist, etapas, quitar=True):

        # Las edades y las poblaciones actuales de las etapas que transicionan.
        edades = símismo._edades[símismo.rebanar(etapas)]
        pobs = símismo._pobs[símismo.rebanar(etapas)]

        # Calcualar la probabilidad de transición.
        dens_cum_eds = dist.cdf(edades)
        probs = np.divide(
            np.subtract(dist.cdf(edades + cambio_edad), dens_cum_eds),
            np.subtract(1, dens_cum_eds)
        )

        probs[np.isnan(probs)] = 1

        # Calcular el número que transicionan.
        n_cambian = np.multiply(pobs, probs)

        # Aplicar el cambio de edad.
        símismo._edades[símismo.rebanar(etapas)] += cambio_edad

        # Si hay que quitar las etapas que transicionario, hacerlo aquí.
        if quitar:
            símismo._pobs[símismo.rebanar(etapas)] -= n_cambian

        # Agregar las transiciones a la matriz de egresos.
        return np.sum(n_cambian, axis=símismo._dims.í_eje('coh'))

    def rebanar(símismo, etapas):
        return símismo._dims.rebanar({'etapa': símismo.í_etapas(etapas)})

    def í_etapas(símismo, etapas):
        return [símismo._etps.index(etp) for etp in etapas]
