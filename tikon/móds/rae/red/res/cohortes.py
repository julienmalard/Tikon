import numpy as np
import xarray as xr
from tikon.móds.rae.utils import EJE_COH, EJE_ETAPA, RES_COHORTES, RES_POBS
from tikon.utils import EJE_PARÁMS

from .res import ResultadoRed


class ResCohortes(ResultadoRed):
    nombre = RES_COHORTES
    líms = (0, None)

    def __init__(símismo, sim, coords, vars_interés):
        símismo.n_coh = sim.exper.controles['n_cohortes']
        coords = {
            EJE_COH: range(símismo.n_coh),
            EJE_ETAPA: [str(etp) for etp in sim.etapas if etp.con_cohortes(exper=sim.simul_exper.exper)],
            'comp': ['pobs', 'edad'],
            **coords
        }
        símismo.activa = len(coords[EJE_ETAPA]) > 0
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

        símismo._m_pobs = símismo.datos.loc[{'comp': 'pobs'}].values
        símismo._m_edad = símismo.datos.loc[{'comp': 'edad'}].values
        símismo._eje_coh = símismo.datos.dims.index(EJE_COH)

    def iniciar(símismo):
        super().iniciar()
        símismo.agregar(símismo.sim[RES_POBS].datos)

    def agregar(símismo, nuevos, edad=0):
        if not símismo.activa:
            return

        í_orig, í_etapas = símismo._índices_etp(nuevos[EJE_ETAPA].values)
        if not í_etapas.size:
            return

        # Limpiar edades de cohortes
        símismo._m_edad[símismo._m_pobs == 0] = 0

        edad = edad.values if isinstance(edad, xr.DataArray) else edad
        símismo._agregar(nuevos[{EJE_ETAPA: í_orig}].values, í_etapas, edad=edad)

    def _agregar(símismo, nuevos, í_etapas, edad):
        # Las edades y poblaciones actuales de las etapas correspondientes

        edades = símismo._m_edad[:, í_etapas]
        pobs = símismo._m_pobs[:, í_etapas]

        # Los cohortes que tienen la diferencia mínima con las nuevas edades.
        # Si hay más que un cohorte con la diferencia mínima, tomará el primero.
        if isinstance(edad, xr.DataArray):
            edad = edad.values
        cohs = np.expand_dims(
            np.where(pobs > 0, 0, np.abs(edades - edad)).argmin(símismo._eje_coh), axis=símismo._eje_coh
        )

        # Las edades de los cohortes con las edades mínimas.
        eds_mín = np.take_along_axis(edades, cohs, axis=símismo._eje_coh)

        # Las poblaciones que corresponden a estas edades mínimas.
        pobs_mín = np.take_along_axis(pobs, cohs, axis=símismo._eje_coh)

        # Dónde no hay población existente, reinicializamos la edad.
        eds_mín = np.where(pobs_mín == 0, [0], eds_mín)

        # Calcular el peso de las edades existentes, según sus poblaciones existentes (para combinar con el nuevo
        # cohorte si hay que combinarlo con un cohorte existente).
        peso_ed_ya = np.divide(pobs_mín, np.add(nuevos, pobs_mín))
        peso_ed_ya[np.isnan(peso_ed_ya)] = 0

        # Los edades promedios. Si no había necesidad de combinar cohortes, será la población del nuevo cohorte.
        eds_prom = eds_mín * peso_ed_ya + edad * (1 - peso_ed_ya)

        # Guardar las edades actualizadas en los índices apropiados
        np.put_along_axis(edades, cohs, eds_prom, axis=símismo._eje_coh)

        # Guardar las poblaciones actualizadas en los índices apropiados
        np.put_along_axis(pobs, cohs, nuevos + pobs_mín, axis=símismo._eje_coh)

        símismo._m_edad[:, í_etapas] = edades
        símismo._m_pobs[:, í_etapas] = pobs

    def quitar(símismo, para_quitar, recips=None):
        if not símismo.activa:
            return

        í_orig, í_etapas = símismo._índices_etp(para_quitar[EJE_ETAPA].values)
        if not í_etapas.size:
            return
        para_quitar = para_quitar[{EJE_ETAPA: í_orig}].values
        pobs = símismo._m_pobs[:, í_etapas]

        totales_pobs = pobs.sum(axis=símismo._eje_coh)
        quitar = np.floor(pobs * (para_quitar / totales_pobs))
        quitar[np.isnan(quitar)] = 0

        pobs = pobs - quitar
        v_para_quitar = para_quitar - quitar.sum(axis=símismo._eje_coh)

        cum_presente = (pobs > 0).cumsum(axis=símismo._eje_coh)
        quitar_res = np.where((pobs > 0) & (cum_presente <= v_para_quitar), 1, 0)

        símismo._m_pobs[:, í_etapas] = pobs - quitar_res

        # Si transiciona a otro cohorte (de otra etapa), implementarlo aquí
        if recips is not None:
            quitar += quitar_res
            edades = símismo._m_edad[:, í_etapas]

            _, í_recips = símismo._índices_etp(recips)

            # Para cada cohorte...
            for í_coh in range(símismo.n_coh):
                símismo._agregar(quitar[í_coh], í_etapas=í_recips, edad=edades[í_coh])

    def ajustar(símismo, cambio):
        if not símismo.activa:
            return
        # Detectar dónde el cambio es positivo y dónde es negativo
        positivos = cambio.copy()
        positivos.values[:] = np.where(cambio.values > 0, cambio.values, 0)
        negativos = cambio.copy()
        negativos.values[:] = np.where(cambio.values < 0, -cambio.values, 0)

        # Agregar los positivos...
        if positivos.values.sum():
            símismo.agregar(positivos)

        # ...y quitar los negativos.
        if negativos.values.sum():
            símismo.quitar(negativos)

    def trans(símismo, cambio_edad, dist):

        í_orig, í_etapas = símismo._índices_etp(cambio_edad[EJE_ETAPA].values)
        if not í_etapas.size:
            return
        cambio_edad = cambio_edad[{EJE_ETAPA: í_orig}]

        # Las edades y las poblaciones actuales de las etapas que transicionan.
        edades = símismo.datos.variable[:, í_etapas, 1]
        pobs = símismo.datos.variable[:, í_etapas, 0]

        # Calcular la probabilidad de transición. Cambiamos a numpy temporalmente
        dims = [d for d in edades.dims if d not in (EJE_ETAPA, EJE_PARÁMS)] + [EJE_ETAPA, EJE_PARÁMS]
        dens_cum_eds = dist.cdf(edades.transpose(*dims))
        probs = (dist.cdf((edades + cambio_edad).transpose(*dims)) - dens_cum_eds) / (1 - dens_cum_eds)

        probs[np.isnan(probs)] = 1

        # Calcular el número que transicionan. Ya estamos con xarray de nuevo.
        probs = xr.Variable(dims, data=probs)
        n_cambian = (pobs * probs).round()

        # Aplicar el cambio de edad y quitar las etapas que transicionaron.
        símismo._m_pobs[:, í_etapas] -= n_cambian.values
        símismo._m_edad[:, í_etapas] += cambio_edad.values

        # Devolver el total de transiciones por etapa
        coords = {dim: símismo.datos.coords[dim] if dim != EJE_ETAPA else cambio_edad[EJE_ETAPA] for dim in pobs.dims}
        return xr.DataArray(n_cambian, coords=coords).sum(dim=EJE_COH)

    def dens_dif(símismo, cambio_edad, dist):

        # Las edades y las poblaciones actuales de las etapas de interés.
        í_orig, í_etapas = símismo._índices_etp(cambio_edad[EJE_ETAPA].values)
        if not í_etapas.size:
            return

        cambio_edad = cambio_edad[{EJE_ETAPA: í_orig}]
        # Las edades y las poblaciones actuales de las etapas que transicionan.
        edades = símismo.datos.variable[:, í_etapas, 1]
        pobs = símismo.datos.variable[:, í_etapas, 0]

        # Calcular la densidad de probabilidad. Cambiamos a numpy temporalmented
        dims = [d for d in edades.dims if d not in (EJE_ETAPA, EJE_PARÁMS)] + [EJE_ETAPA, EJE_PARÁMS]
        dens_cum_eds = dist.cdf(edades.transpose(*dims))
        dens_con_cambio = dist.cdf((edades + cambio_edad).transpose(*dims))
        dens = xr.Variable(dims, data=dens_con_cambio - dens_cum_eds)

        coords = {dim: símismo.datos.coords[dim] if dim != EJE_ETAPA else cambio_edad[EJE_ETAPA] for dim in pobs.dims}
        return xr.DataArray(pobs * dens, coords=coords).sum(dim=EJE_COH)  # Devolver en formato xarray

    def _índices_etp(símismo, etapas):
        í_orig, í_etps = list(
            zip(*[(
                í, np.argwhere(símismo.datos.indexes[EJE_ETAPA] == x)[0, 0]) for í, x in enumerate(etapas)
                if x in símismo.datos.indexes[EJE_ETAPA]
            ])
        )
        return np.array(í_orig), np.array(í_etps)
