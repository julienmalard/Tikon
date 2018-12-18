import numpy as np

from tikon.rsltd.res import DimsCoh


class Cohortes(object):
    def __init__(símismo, etapas, n_rep_estoc, n_rep_parám, parc):
        símismo._etps, símismo.í_etps = zip(*[(etp, í) for í, etp in enumerate(etapas) if etp.con_cohortes()])

        símismo._dims = DimsCoh(n_coh=10, n_estoc=n_rep_estoc, n_parám=n_rep_parám, parc=parc, etapas=símismo._etps)

        símismo._pobs = np.zeros(símismo._dims.frm())
        símismo._edades = np.zeros(símismo._dims.frm())

    def agregar(símismo, nuevos, edad=0, etapas=None):

        # Limpiar edades de cohortes
        símismo._edades[símismo._pobs == 0] = 0

        if etapas is None:
            rbn = slice(None)
            nuevos = símismo._proc_matr_datos(nuevos)
        else:
            rbn = símismo.rebanar(etapas)

        # Las edades y las poblaciones actuales de las etapas
        pobs = símismo._pobs[rbn]
        edades = símismo._edades[rbn]

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

        símismo._pobs[rbn] = pobs
        símismo._edades[rbn] = edades

    def quitar(símismo, para_quitar, etapas=None, recips=None):

        if etapas is None:
            rbn = slice(None)
            para_quitar = símismo._proc_matr_datos(para_quitar)
        else:
            rbn = símismo.rebanar(etapas)

        pobs = símismo._pobs[rbn]
        edades = símismo._edades[rbn]

        eje_coh = símismo.eje_coh()

        totales_pobs = np.sum(pobs, axis=0)
        quitar = np.floor(np.divide(para_quitar, totales_pobs) * pobs)
        quitar[np.isnan(quitar)] = 0

        # para hacer: combinar quitar y quitar2
        np.subtract(pobs, quitar, out=pobs)

        para_quitar = np.subtract(para_quitar, quitar.sum(axis=eje_coh))

        cum_presente = np.cumsum(np.greater(pobs, 0), axis=eje_coh)
        quitar_2 = np.where(
            np.logical_and(np.greater(pobs, 0), np.less_equal(cum_presente, para_quitar)),
            1,
            0
        )

        símismo._pobs[rbn] = np.subtract(pobs, quitar_2)

        # Si transiciona a otro cohorte (de otra etapa), implementarlo aquí
        if recips is not None:
            np.add(quitar_2, quitar, out=quitar)

            # Para cada cohorte...
            for í_coh in range(pobs.shape[eje_coh]):
                # Las edades de las etapas que se quitaron
                eds = edades[í_coh, ...]  # para hacer: rebanar mejor

                # Cambiar el orden de las etapas para los cohortes recipientes
                símismo.agregar(quitar[í_coh], edad=eds, etapas=recips[0])

    def ajustar(símismo, cambio, etapas=None):
        # Detectar dónde el cambio es positivo y dónde es negativo
        positivos = np.where(cambio > 0, cambio, [0])
        negativos = np.where(cambio < 0, -cambio, [0])

        # Agregar los positivos...
        símismo.agregar(positivos, etapas=etapas)

        # ...y quitar los negativos.
        símismo.quitar(negativos, etapas=etapas)

    def trans(símismo, cambio_edad, dist, etapas, quitar=True):

        # Las edades y las poblaciones actuales de las etapas que transicionan.
        rbn = símismo.rebanar(etapas)
        edades = símismo._edades[rbn]
        pobs = símismo._pobs[rbn]

        # Calcualar la probabilidad de transición.
        dens_cum_eds = dist.cdf(edades)
        probs = np.divide(
            np.subtract(dist.cdf(edades + cambio_edad), dens_cum_eds),
            np.subtract(1, dens_cum_eds)
        )

        probs[np.isnan(probs)] = 1

        # Calcular el número que transicionan.
        n_cambian = np.round(np.multiply(pobs, probs))

        # Aplicar el cambio de edad.
        símismo._edades[rbn] += cambio_edad

        # Si hay que quitar las etapas que transicionario, hacerlo aquí.
        if quitar:
            símismo._pobs[rbn] -= n_cambian

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
            datos = datos[..., símismo.í_etps]  # para hacer: rebanar mejor

        return datos
