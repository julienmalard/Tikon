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
            EJE_ETAPA: [str(etp) for etp in sim.etapas if etp.con_cohortes(exper=sim.simul_exper.exper)],
            EJE_COH: range(símismo.n_coh),
            'comp': ['pobs', 'edad'],
            **coords
        }
        símismo.activa = len(coords[EJE_ETAPA]) > 0
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

        símismo.pobs = símismo.datos.loc[{'comp': 'pobs'}]
        símismo.edad = símismo.datos.loc[{'comp': 'edad'}]

    def iniciar(símismo):
        super().iniciar()
        símismo.agregar(símismo.sim[RES_POBS].datos)

    def agregar(símismo, nuevos, edad=0):
        if not símismo.activa:
            return

        # Limpiar edades de cohortes
        símismo.edad.variable[:] = símismo.edad.where(símismo.pobs == 0, 0)

        etps_nuevos = símismo._índices_etp(nuevos[EJE_ETAPA].values)
        if not etps_nuevos.size:
            return

        símismo._agregar(nuevos.variable, etps_nuevos, edad=edad)

    def _agregar(símismo, nuevos, etps_nuevos, edad):
        # Las edades y poblaciones actuales de las etapas correspondientes

        edades = símismo.edad.variable[{EJE_ETAPA: etps_nuevos}]
        pobs = símismo.pobs.variable[{EJE_ETAPA: etps_nuevos}]

        # Los cohortes que tienen la diferencia mínima con las nuevas edades.
        # Si hay más que un cohorte con la diferencia mínima, tomará el primero.
        if isinstance(edad, xr.DataArray):
            edad = edad.variable
        cohs = np.abs(edades - edad).where(pobs > 0, 0).argmin(EJE_COH)

        eds_mín = edades[{EJE_COH: cohs}]
        pobs_corresp = pobs[{EJE_COH: cohs}]

        # Calcular el peso de las edades existentes, según sus poblaciones existentes (para combinar con el nuevo
        # cohorte si hay que combinarlo con un cohorte existente).
        peso_ed_ya = (pobs_corresp / (nuevos + pobs_corresp)).fillna(0)

        # Los edades promedios. Si no había necesidad de combinar cohortes, será la población del nuevo cohorte.
        eds_prom = eds_mín * peso_ed_ya + edad * (1 - peso_ed_ya)

        # Guardar las poblaciones y edades actualizadas en los índices apropiados
        símismo.datos[{'comp': 0, EJE_ETAPA: etps_nuevos, EJE_COH: cohs}] = nuevos + pobs_corresp
        símismo.datos[{'comp': 1, EJE_ETAPA: etps_nuevos, EJE_COH: cohs}] = eds_prom

    def quitar(símismo, para_quitar, recips=None):
        if not símismo.activa:
            return

        etps_quitar = símismo._índices_etp(para_quitar[EJE_ETAPA].values)
        if not etps_quitar.size:
            return

        pobs = símismo.pobs.variable[{EJE_ETAPA: etps_quitar}]

        v_para_quitar = para_quitar.variable

        totales_pobs = pobs.sum(dim=EJE_COH)
        quitar = np.floor(pobs * (v_para_quitar / totales_pobs))
        quitar = quitar.fillna(0)

        pobs = pobs - quitar
        v_para_quitar = v_para_quitar - quitar.sum(dim=EJE_COH)

        cum_presente = (pobs > 0).cumsum(dim=EJE_COH)
        quitar_res = xr.where((pobs > 0) & (cum_presente <= v_para_quitar), 1, 0)

        símismo.pobs.variable[{EJE_ETAPA: etps_quitar}] = pobs - quitar_res

        # Si transiciona a otro cohorte (de otra etapa), implementarlo aquí
        if recips is not None:
            quitar += quitar_res
            edades = símismo.edad.variable[{EJE_ETAPA: etps_quitar}]

            í_recips = símismo._índices_etp(recips)

            # Para cada cohorte...
            for í_coh in range(símismo.n_coh):
                símismo._agregar(quitar[{EJE_COH: í_coh}], etps_nuevos=í_recips, edad=edades[{EJE_COH: í_coh}])

    def ajustar(símismo, cambio):
        if not símismo.activa:
            return
        # Detectar dónde el cambio es positivo y dónde es negativo
        positivos = xr.where(cambio > 0, cambio, 0)
        negativos = xr.where(cambio < 0, -cambio, 0)

        # Agregar los positivos...
        if positivos.sum():
            símismo.agregar(positivos)

        # ...y quitar los negativos.
        if negativos.sum():
            símismo.quitar(negativos)

    def trans(símismo, cambio_edad, dist):

        etps_trans = símismo._índices_etp(cambio_edad[EJE_ETAPA].values)
        if not etps_trans.size:
            return

        # Las edades y las poblaciones actuales de las etapas que transicionan.
        datos = símismo.datos.variable[{EJE_ETAPA: etps_trans}]
        edades = datos[{'comp': 1}]
        pobs = datos[{'comp': 0}]

        # Calcular la probabilidad de transición. Cambiamos a numpy temporalmente
        dims = [d for d in edades.dims if d not in (EJE_ETAPA, EJE_PARÁMS)] + [EJE_ETAPA, EJE_PARÁMS]
        dens_cum_eds = dist.cdf(edades.transpose(*dims))
        probs = (dist.cdf((edades + cambio_edad).transpose(*dims)) - dens_cum_eds) / (1 - dens_cum_eds)

        probs[np.isnan(probs)] = 1

        # Calcular el número que transicionan. Ya estamos con xarray de nuevo.
        probs = xr.Variable(dims, data=probs)
        n_cambian = (pobs * probs).round()

        # Aplicar el cambio de edad y quitar las etapas que transicionaron.
        símismo.pobs.variable[{EJE_ETAPA: etps_trans}] -= n_cambian
        símismo.edad.variable[{EJE_ETAPA: etps_trans}] += cambio_edad.variable

        # Devolver el total de transiciones por etapa
        coords = {dim: símismo.datos.coords[dim] if dim != EJE_ETAPA else cambio_edad[EJE_ETAPA] for dim in pobs.dims}
        return xr.DataArray(n_cambian, coords=coords).sum(dim=EJE_COH)

    def dens_dif(símismo, cambio_edad, dist):

        # Las edades y las poblaciones actuales de las etapas de interés.
        etps_dif = símismo._índices_etp(cambio_edad[EJE_ETAPA].values)
        if not etps_dif.size:
            return

        # Las edades y las poblaciones actuales de las etapas que transicionan.
        edades = símismo.edad[{EJE_ETAPA: etps_dif}]
        pobs = símismo.pobs[{EJE_ETAPA: etps_dif}]

        # Calcular la densidad de probabilidad. Cambiamos a numpy temporalmented
        dims = [d for d in edades.dims if d not in (EJE_ETAPA, EJE_PARÁMS)] + [EJE_ETAPA, EJE_PARÁMS]
        dens_cum_eds = dist.cdf(edades.transpose(*dims))
        dens_con_cambio = dist.cdf((edades + cambio_edad).transpose(*dims))
        dens = xr.Variable(dims, data=dens_con_cambio - dens_cum_eds)

        coords = {dim: símismo.datos.coords[dim] if dim != EJE_ETAPA else cambio_edad[EJE_ETAPA] for dim in pobs.dims}
        return xr.DataArray(pobs * dens, coords=coords).sum(dim=EJE_COH)  # Devolver en formato xarray

    def _índices_etp(símismo, etapas):
        return np.array(
            [np.argwhere(símismo.datos.indexes[EJE_ETAPA] == x)[0, 0] for x in etapas if
             x in símismo.datos.indexes[EJE_ETAPA]]
        )
