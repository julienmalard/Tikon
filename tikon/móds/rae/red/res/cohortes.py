import numpy as np
import xarray as xr
from tikon.móds.rae.red.res.res import ResultadoRed
from tikon.móds.rae.red.utils import EJE_COH, EJE_ETAPA, RES_COHORTES


class ResCohortes(ResultadoRed):
    n_coh = 10
    nombre = RES_COHORTES

    def __init__(símismo, sim, coords):
        coords = {
            EJE_ETAPA: [etp for etp in sim.etapas if etp.con_cohortes()],
            EJE_COH: range(símismo.n_coh),
            'comp': ['pobs', 'edad'],
            **coords
        }
        super().__init__(sim=sim, coords=coords)

        símismo.pobs = símismo.datos.loc[{'comp': 'pobs'}]
        símismo.edad = símismo.datos.loc[{'comp': 'edad'}]

        símismo._eje_coh = símismo.datos.dims.index('coh')

    def agregar(símismo, nuevos, edad=0):

        # Limpiar edades de cohortes
        símismo.edad[símismo.pobs == 0] = 0

        índ = {EJE_ETAPA: nuevos[EJE_ETAPA]}

        # Las edades y las poblaciones actuales de las etapas
        pobs = símismo.pobs.loc[índ]
        edades = símismo.edad.loc[índ]

        eje_coh = símismo._eje_coh

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

        símismo.pobs.loc[índ] = pobs
        símismo.edad.loc[índ] = edades

    def quitar(símismo, para_quitar, recips=None):

        índ = {EJE_ETAPA: para_quitar[EJE_ETAPA]}

        pobs = símismo.pobs[índ]
        edades = símismo.edad[índ]

        eje_coh = símismo._eje_coh

        totales_pobs = pobs.sum(dim='coh')
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

        símismo.pobs.loc[índ] = np.subtract(pobs, quitar_2)

        # Si transiciona a otro cohorte (de otra etapa), implementarlo aquí
        if recips is not None:
            np.add(quitar_2, quitar, out=quitar)

            # Para cada cohorte...
            for í_coh in range(pobs.shape[eje_coh]):
                # Las edades de las etapas que se quitaron
                eds = edades[í_coh, ...]  # para hacer: rebanar mejor

                # Cambiar el orden de las etapas para los cohortes recipientes
                símismo.agregar(quitar[í_coh], edad=eds, etapas=recips[0])

    def ajustar(símismo, cambio):
        # Detectar dónde el cambio es positivo y dónde es negativo
        positivos = xr.where(cambio > 0, cambio, 0)
        negativos = xr.where(cambio < 0, cambio, 0)

        # Agregar los positivos...
        símismo.agregar(positivos)

        # ...y quitar los negativos.
        símismo.quitar(negativos)

    def trans(símismo, cambio_edad, dist, quitar=True):

        # Las edades y las poblaciones actuales de las etapas que transicionan.
        índ = {EJE_ETAPA: cambio_edad[EJE_ETAPA]}
        edades = símismo.edad.loc[índ]
        pobs = símismo.pobs.loc[índ]

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
        símismo.edad.loc[índ] += cambio_edad

        # Si hay que quitar las etapas que transicionario, hacerlo aquí.
        if quitar:
            símismo.pobs.loc[índ] -= n_cambian

        # Agregar las transiciones a la matriz de egresos.
        return n_cambian.sum(dim='coh')
