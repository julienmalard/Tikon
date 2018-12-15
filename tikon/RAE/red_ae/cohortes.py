import numpy as np

from tikon.rsltd.res import DimsCoh


class Cohortes(object):
    def __init__(símismo, etapas, n_rep_estoc, n_rep_parám, parc):
        símismo._etps, símismo.í_etps = zip(*[(etp, í) for í, etp in enumerate(etapas) if etp.con_cohortes()])

        símismo._dims = DimsCoh(n_coh=10, n_estoc=n_rep_estoc, n_parám=n_rep_parám, parc=parc, etapas=símismo._etps)

        símismo._pobs = np.zeros(símismo._dims.frm())
        símismo._edades = np.zeros(símismo._dims.frm())

    def agregar(símismo, nuevos, edad=0):

        nuevos = símismo._proc_matr_datos(nuevos)

        # Limpiar edades de cohortes
        símismo._edades[símismo._pobs == 0] = 0

        # Las edades y las poblaciones actuales de las etapas
        edades = símismo._edades
        pobs = símismo._pobs
        eje_coh = símismo.eje_coh()

        # Los índices de los días cuyos cohortes tienen la edad mínima. Si hay más que un día (cohorte) con la
        # edad mínima, tomará el primero.
        í_cohs = np.expand_dims(np.argmin(edades, axis=eje_coh), axis=eje_coh)

        # Las edades de los cohortes con las edades mínimas.
        eds_mín = np.take_along_axis(edades, í_cohs, axis=eje_coh)

        # Las poblaciones que corresponden a estas edades mínimas.
        pobs_coresp = np.take_along_axis(pobs, í_cohs, axis=eje_coh)

        # Dónde no hay población existente, reinicializamos la edad.
        eds_mín = np.where(pobs_coresp == 0, [0], eds_mín)

        # Calcular el peso de las edades existentes, según sus poblaciones existentes (para combinar con el nuevo
        # cohorte si hay que combinarlo con un cohorte existente).
        peso_ed_ya = np.divide(pobs_coresp, np.add(nuevos, pobs_coresp))
        peso_ed_ya[np.isnan(peso_ed_ya)] = 0

        # Los edades promedios. Si no había necesidad de combinar cohortes, será la población del nuevo cohorte.
        eds_prom = np.add(np.multiply(eds_mín, peso_ed_ya), np.multiply(edad, np.subtract(1, peso_ed_ya)))

        # Guardar las edades actualizadas en los índices apropiados
        np.put_along_axis(edades, í_cohs, eds_prom, axis=eje_coh)

        # Guardar las poblaciones actualizadas en los índices apropiados
        np.put_along_axis(pobs, í_cohs, nuevos + pobs_coresp, axis=eje_coh)

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
        return np.sum(n_cambian, axis=símismo.eje_coh())

    def rebanar(símismo, etapas):
        return símismo._dims.rebanar({'etapa': símismo.í_etapas(etapas)})

    def í_etapas(símismo, etapas):
        return [símismo._etps.index(etp) for etp in etapas]

    def eje_coh(símismo):
        return símismo._dims.í_eje('coh')

    def _proc_matr_datos(símismo, datos):

        n_etps = datos.shape[-1]
        if n_etps != len(símismo._etps):
            datos = datos[..., símismo.í_etps]

        return datos
