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

    def agregar(símismo, nuevos, edad=0):

        # Limpiar edades de cohortes
        símismo.edad[:] = símismo.edad.where(símismo.pobs == 0, 0)

        índ = {EJE_ETAPA: nuevos[EJE_ETAPA]}

        # Las edades actuales de las etapas
        datos = símismo.datos.loc[índ]
        edades = datos['edad']

        # Los cohortes que tienen la diferencia mínima con las nuevas edades.
        # Si hay más que un cohorte con la diferencia mínima, tomará el primero.
        dif_edades = (edades - edad).abs()
        datos_dif_mín = datos[{EJE_COH: dif_edades.argmin(EJE_COH)}].drop(EJE_COH)

        eds_mín = datos_dif_mín.loc[{'comp': 'edad'}]
        pobs_coresp = datos_dif_mín.loc[{'comp': 'pobs'}]

        # Calcular el peso de las edades existentes, según sus poblaciones existentes (para combinar con el nuevo
        # cohorte si hay que combinarlo con un cohorte existente).
        peso_ed_ya = (pobs_coresp / (nuevos + pobs_coresp)).fillna(0)

        # Los edades promedios. Si no había necesidad de combinar cohortes, será la población del nuevo cohorte.
        eds_prom = eds_mín * peso_ed_ya + edad * (1 - peso_ed_ya)

        # Guardar las poblaciones y edades actualizadas en los índices apropiados
        símismo.pobs.loc[índ] = nuevos + pobs_coresp
        símismo.edad.loc[índ] = eds_prom

    def quitar(símismo, para_quitar, recips=None):

        índ = {EJE_ETAPA: para_quitar[EJE_ETAPA]}

        pobs = símismo.pobs[índ]
        edades = símismo.edad[índ]

        totales_pobs = pobs.sum(dim=EJE_COH)
        quitar = (pobs * (para_quitar / totales_pobs)).floor()
        quitar = quitar.fillna(0)

        pobs = pobs - quitar
        para_quitar = para_quitar - quitar.sum(dim=EJE_COH)

        cum_presente = (pobs > 0).cumsum(dim=EJE_COH)
        quitar_res = xr.where((pobs > 0) & (cum_presente <= para_quitar), 1, 0)

        símismo.pobs.loc[índ] = pobs - quitar_res

        # Si transiciona a otro cohorte (de otra etapa), implementarlo aquí
        if recips is not None:
            quitar += quitar_res
            quitar[EJE_ETAPA] = recips

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

    def trans(símismo, cambio_edad, dist, quitar=True):

        # Las edades y las poblaciones actuales de las etapas que transicionan.
        índ = cambio_edad.coords
        edades = símismo.edad.loc[índ]
        pobs = símismo.pobs.loc[índ]

        # Calcular la probabilidad de transición. Cambiamos a numpy temporalmente
        dens_cum_eds = dist.cdf(edades)
        probs = (dist.cdf(edades + cambio_edad) - dens_cum_eds) / (1 - dens_cum_eds)

        probs[np.isnan(probs)] = 1

        # Calcular el número que transicionan. Ya estamos con xarray de nuevo.
        n_cambian = (pobs * probs).round()

        # Aplicar el cambio de edad.
        símismo.edad.loc[índ] += cambio_edad

        # Si hay que quitar las etapas que transicionario, hacerlo aquí.
        if quitar:
            símismo.pobs.loc[índ] -= n_cambian

        # Devolver el total de transiciones por etapa
        return n_cambian.sum(dim=EJE_COH)
