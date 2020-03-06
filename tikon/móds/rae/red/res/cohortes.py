import math as mat

import numpy as np

from tikon.datos.datos import donde, Datos, alinear_como
from tikon.móds.rae.orgs.ecs.utils import ECS_TRANS
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
            EJE_ETAPA: [etp for etp in sim.etapas if etp.con_cohortes(exper=sim.simul_exper.exper)],
            'comp': ['pobs', 'edad'],
            **coords
        }
        símismo.activa = len(coords[EJE_ETAPA]) > 0
        super().__init__(sim=sim, coords=coords, vars_interés=vars_interés)

    @property
    def pobs(símismo):
        return símismo.datos.loc[{'comp': 'pobs'}].dejar('comp')

    @pobs.setter
    def pobs(símismo, val):
        crds = val.coords if isinstance(val, Datos) else {}
        símismo.datos.loc[{'comp': 'pobs', **crds}] = val

    @property
    def edad(símismo):
        return símismo.datos.loc[{'comp': 'edad'}].dejar('comp')

    @edad.setter
    def edad(símismo, val):
        crds = val.coords if isinstance(val, Datos) else {}
        símismo.datos.loc[{'comp': 'edad', **crds}] = val

    def iniciar(símismo):
        super().iniciar()
        pobs = símismo.sim[RES_POBS].datos
        n = mat.ceil(símismo.n_coh / 2)

        try:
            ecs_prob = símismo.sim.simul_exper.ecs['red'][ECS_TRANS]['Prob']
            for ec_prob in ecs_prob:
                máx = ec_prob.dist.ppf(0.99)
                cosos = ec_prob.cosos
                pobs_etps = pobs.loc[{EJE_ETAPA: cosos}]
                pobs_n = pobs_etps // n
                extras = pobs_etps % n
                for í, ed in enumerate(np.linspace(0, máx, num=n)):
                    edades = Datos(
                        ed, dims=[EJE_ETAPA, EJE_PARÁMS],
                        coords={EJE_ETAPA: cosos, EJE_PARÁMS: range(símismo.sim.simul_exper.reps['paráms'])}
                    )
                    símismo.agregar(pobs_n + (í < extras), edad=edades)

        except KeyError:
            símismo.agregar(pobs)

    def agregar(símismo, nuevos, edad=0):

        etps_nuevos = [x for x in nuevos.coords[EJE_ETAPA] if x in símismo.datos.coords[EJE_ETAPA]]
        if not etps_nuevos:
            return
        índs = {EJE_ETAPA: etps_nuevos}
        nuevos = nuevos.loc[índs]

        # Limpiar edades de cohortes
        símismo.edad = donde(símismo.pobs == 0, 0, símismo.edad)

        # Las edades y poblaciones actuales de las etapas correspondientes
        edades = símismo.edad.loc[índs]
        pobs = símismo.pobs.loc[índs]

        # Los cohortes que tienen la diferencia mínima con las nuevas edades.
        # Si hay más que un cohorte con la diferencia mínima, tomará el primero.
        dif_edades = abs(edades - edad).donde(pobs > 0, 0)
        í_eje_coh = dif_edades.dims.index(EJE_COH)
        cohs = np.expand_dims(dif_edades.f_eje(np.argmin, dim=EJE_COH).matr, axis=í_eje_coh)
        eds_mín = edades.nuevo_como(
            np.take_along_axis(edades.matr, indices=cohs, axis=í_eje_coh).squeeze(í_eje_coh), excluir=EJE_COH
        )
        pobs_corresp = pobs.nuevo_como(
            np.take_along_axis(pobs.matr, indices=cohs, axis=í_eje_coh).squeeze(í_eje_coh), excluir=EJE_COH
        )
        nuevos = alinear_como(como=pobs_corresp, otro=nuevos)  # Necesario para `put_along_axis` después.

        # Calcular el peso de las edades existentes, según sus poblaciones existentes (para combinar con el nuevo
        # cohorte si hay que combinarlo con un cohorte existente).
        peso_ed_ya = (pobs_corresp / (nuevos + pobs_corresp)).llenar_nan(0)

        # Los edades promedios. Si no había necesidad de combinar cohortes, será la población del nuevo cohorte.
        eds_prom = eds_mín * peso_ed_ya + edad * (1 - peso_ed_ya)

        np.put_along_axis(edades.matr, cohs, values=eds_prom.matr, axis=í_eje_coh)
        np.put_along_axis(pobs.matr, cohs, values=(nuevos + pobs_corresp).matr, axis=í_eje_coh)

        # Guardar las poblaciones y edades actualizadas en los índices apropiados
        símismo.pobs = pobs
        símismo.edad = edades

    def quitar(símismo, para_quitar, recips=None):
        if not símismo.activa:
            return

        etps_quitar = [x for x in para_quitar.coords[EJE_ETAPA] if x in símismo.datos.coords[EJE_ETAPA]]
        if not etps_quitar:
            if recips:
                raise ValueError('Etapas para quitar no tienen cohortes.')
            return
        índs = {EJE_ETAPA: etps_quitar}
        para_quitar = para_quitar.loc[índs]
        pobs = símismo.pobs.loc[índs]
        edades = símismo.edad.loc[índs]

        totales_pobs = pobs.suma(dim=EJE_COH)
        quitar = (pobs * (para_quitar / totales_pobs)).fi(np.floor).llenar_nan(0)

        pobs = pobs - quitar
        para_quitar = para_quitar - quitar.suma(dim=EJE_COH)

        cum_presente = (pobs > 0).f_eje(np.cumsum, dim=EJE_COH)
        quitar_res = donde((pobs > 0) & (cum_presente <= para_quitar), 1, 0)

        símismo.pobs.loc[índs] = pobs - quitar_res

        # Si transiciona a otro cohorte (de otra etapa), implementarlo aquí
        if recips is not None:
            quitar += quitar_res
            quitar.coords[EJE_ETAPA] = recips
            edades.coords[EJE_ETAPA] = recips

            # Para cada cohorte...
            for í_coh in range(símismo.n_coh):
                símismo.agregar(quitar[{EJE_COH: í_coh}], edad=edades[{EJE_COH: í_coh}])

    def ajustar(símismo, cambio):
        if not símismo.activa:
            return
        # Detectar dónde el cambio es positivo y dónde es negativo
        positivos = donde(cambio > 0, cambio, 0)
        negativos = donde(cambio < 0, -cambio, 0)

        # Agregar los positivos...
        if positivos.suma():
            símismo.agregar(positivos)

        # ...y quitar los negativos.
        if negativos.suma():
            símismo.quitar(negativos)

    def trans(símismo, cambio_edad, dist):

        # Las edades y las poblaciones actuales de las etapas que transicionan.
        índ = cambio_edad.coords
        edades = símismo.edad.loc[índ]
        pobs = símismo.pobs.loc[índ]

        # Calcular la probabilidad de transición. Cambiamos a numpy temporalmente
        dims = [d for d in edades.dims if d not in (EJE_ETAPA, EJE_PARÁMS)] + [EJE_ETAPA, EJE_PARÁMS]
        dens_cum_eds = dist.cdf(edades.transposar(dims).matr)
        probs = (dist.cdf((edades + cambio_edad).transposar(dims).matr) - dens_cum_eds) / (1 - dens_cum_eds)

        # Calcular el número que transicionan. Ya estamos con Datos de nuevo.
        probs = Datos(probs, coords=pobs.coords, dims=dims).llenar_nan(1)
        n_cambian = (pobs * probs).fi(np.round)

        # Aplicar el cambio de edad.
        símismo.edad += cambio_edad

        # Quitar las etapas que transicionario.
        símismo.pobs -= n_cambian

        # Devolver el total de transiciones por etapa
        return n_cambian.suma(dim=EJE_COH)

    def dens_dif(símismo, cambio_edad, dist):

        # Las edades y las poblaciones actuales de las etapas de interés.
        índ = cambio_edad.coords
        edades = símismo.edad.loc[índ]
        pobs = símismo.pobs.loc[índ]

        # Calcular la densidad de probabilidad. Cambiamos a numpy temporalmente
        dims = [d for d in edades.dims if d not in (EJE_ETAPA, EJE_PARÁMS)] + [EJE_ETAPA, EJE_PARÁMS]
        dens_cum_eds = dist.cdf(edades.transposar(dims).matr)
        dens_con_cambio = dist.cdf((edades + cambio_edad).transposar(dims).matr)
        dens = Datos(dens_con_cambio - dens_cum_eds, coords=pobs.coords, dims=dims)

        return (pobs * dens).suma(dim=EJE_COH)  # Devolver en formato Datos

    def cerrar(símismo):
        pass
