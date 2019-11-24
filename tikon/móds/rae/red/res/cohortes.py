import numpy as np
import xarray as xr
from tikon.móds.rae.utils import EJE_COH, EJE_ETAPA, RES_COHORTES, RES_POBS
from tikon.utils import EJE_PARÁMS

from .res import ResultadoRed


class ResCohortes(ResultadoRed):
    nombre = RES_COHORTES

    def __init__(símismo, sim, coords, vars_interés):
        símismo.n_coh = sim.exper.controles['n_cohortes']
        coords = {
            EJE_ETAPA: [etp for etp in sim.etapas if etp.con_cohortes(exper=sim.simul_exper.exper)],
            EJE_COH: range(símismo.n_coh),
            'comp': ['pobs', 'edad'],
            **coords
        }
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

        símismo.pobs = símismo.datos.loc[{'comp': 'pobs'}]
        símismo.edad = símismo.datos.loc[{'comp': 'edad'}]

    def iniciar(símismo):
        super().iniciar()
        símismo.agregar(símismo.sim[RES_POBS].datos)

    def agregar(símismo, nuevos, edad=0):

        # Limpiar edades de cohortes
        símismo.edad[:] = símismo.edad.where(símismo.pobs == 0, 0)

        etps_nuevos = [x for x in nuevos[EJE_ETAPA].values if x in símismo.datos[EJE_ETAPA]]
        if not etps_nuevos:
            return
        índ = {EJE_ETAPA: etps_nuevos}

        # Las edades y poblaciones actuales de las etapas correspondientes
        datos = símismo.datos.loc[índ]
        edades = datos.loc[{'comp': 'edad'}]
        pobs = datos.loc[{'comp': 'pobs'}]

        # Los cohortes que tienen la diferencia mínima con las nuevas edades.
        # Si hay más que un cohorte con la diferencia mínima, tomará el primero.
        dif_edades = np.abs(edades - edad).where(pobs > 0, 0)
        datos_dif_mín = datos[{EJE_COH: dif_edades.argmin(EJE_COH)}].drop(EJE_COH)

        eds_mín = datos_dif_mín.loc[{'comp': 'edad'}]
        pobs_corresp = datos_dif_mín.loc[{'comp': 'pobs'}]

        # Calcular el peso de las edades existentes, según sus poblaciones existentes (para combinar con el nuevo
        # cohorte si hay que combinarlo con un cohorte existente).
        peso_ed_ya = (pobs_corresp / (nuevos + pobs_corresp)).fillna(0)

        # Los edades promedios. Si no había necesidad de combinar cohortes, será la población del nuevo cohorte.
        eds_prom = eds_mín * peso_ed_ya + edad * (1 - peso_ed_ya)

        # Guardar las poblaciones y edades actualizadas en los índices apropiados
        símismo.datos = nuevos + pobs_corresp
        símismo.datos = eds_prom

    def quitar(símismo, para_quitar, recips=None):

        etps_quitar = [x for x in para_quitar[EJE_ETAPA].values if x in símismo.datos[EJE_ETAPA]]
        if not etps_quitar:
            return
        índ = {EJE_ETAPA: etps_quitar}

        pobs = símismo.pobs.loc[índ]
        edades = símismo.edad.loc[índ]

        totales_pobs = pobs.sum(dim=EJE_COH)
        quitar = np.floor(pobs * (para_quitar / totales_pobs))
        quitar = quitar.fillna(0)

        pobs = pobs - quitar
        para_quitar = para_quitar - quitar.sum(dim=EJE_COH)

        cum_presente = (pobs > 0).cumsum(dim=EJE_COH)
        quitar_res = xr.where((pobs > 0) & (cum_presente <= para_quitar), 1, 0)

        símismo.datos = pobs - quitar_res

        # Si transiciona a otro cohorte (de otra etapa), implementarlo aquí
        if recips is not None:
            quitar += quitar_res
            quitar[EJE_ETAPA] = recips
            edades[EJE_ETAPA] = recips

            # Para cada cohorte...
            for í_coh in range(símismo.n_coh):
                símismo.agregar(quitar[{EJE_COH: í_coh}], edad=edades[{EJE_COH: í_coh}])

    def ajustar(símismo, cambio):
        # Detectar dónde el cambio es positivo y dónde es negativo
        positivos = xr.where(cambio > 0, cambio, 0)
        negativos = xr.where(cambio < 0, cambio, 0)

        # Agregar los positivos...
        símismo.agregar(positivos)

        # ...y quitar los negativos.
        símismo.quitar(negativos)

    def trans(símismo, cambio_edad, dist):

        # Las edades y las poblaciones actuales de las etapas que transicionan.
        índ = cambio_edad.coords
        edades = símismo.edad.loc[índ]
        pobs = símismo.pobs.loc[índ]

        # Calcular la probabilidad de transición. Cambiamos a numpy temporalmente
        dims = [d for d in edades.dims if d not in (EJE_ETAPA, EJE_PARÁMS)] + [EJE_ETAPA, EJE_PARÁMS]
        dens_cum_eds = dist.cdf(edades.transpose(*dims))
        probs = (dist.cdf((edades + cambio_edad).transpose(*dims)) - dens_cum_eds) / (1 - dens_cum_eds)

        probs[np.isnan(probs)] = 1

        # Calcular el número que transicionan. Ya estamos con xarray de nuevo.
        probs = xr.DataArray(probs, coords=pobs.coords, dims=dims)
        n_cambian = (pobs * probs).round()

        # Aplicar el cambio de edad.
        símismo.datos += cambio_edad

        # Quitar las etapas que transicionario.
        símismo.datos -= n_cambian

        # Devolver el total de transiciones por etapa
        return n_cambian.sum(dim=EJE_COH).drop('comp')

    def dens_dif(símismo, cambio_edad, dist):

        # Las edades y las poblaciones actuales de las etapas de interés.
        índ = cambio_edad.coords
        edades = símismo.edad.loc[índ]
        pobs = símismo.pobs.loc[índ]

        # Calcular la densidad de probabilidad. Cambiamos a numpy temporalmented
        dims = [d for d in edades.dims if d not in (EJE_ETAPA, EJE_PARÁMS)] + [EJE_ETAPA, EJE_PARÁMS]
        dens_cum_eds = dist.cdf(edades.transpose(*dims))
        dens_con_cambio = dist.cdf((edades + cambio_edad).transpose(*dims))
        dens = xr.DataArray(dens_con_cambio - dens_cum_eds, coords=pobs.coords, dims=dims)

        return (pobs * dens).sum(dim=EJE_COH).drop('comp')  # Devolver en formato xarray
