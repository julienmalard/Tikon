from warnings import warn as avisar

import pandas as pd
from babel.dates import format_date

from tikon.móds.cultivo.extrn import SimulCultivoExterno, InstanciaSimulCultivo
from tikon.móds.cultivo.res import RES_HUMSUELO, RES_BIOMASA
from tikon.móds.rae.utils import EJE_ETAPA, EJE_VÍCTIMA
from tikon.utils import EJE_PARC, EJE_COORD
from .meteo import ProveedorMeteoPCSEPandas


class InstanciaPCSE(InstanciaSimulCultivo):
    _conv_vars = {
        'hoja': ('LAI', 1),
        'raíz': ('WRT', 1 / 10000),
        'palo': ('WST', 1 / 10000),
        'fruta': ('WSO', 1 / 10000)
    }

    def __init__(símismo, sim, índs, reps):
        super().__init__(sim=sim, índs=índs, reps=reps)

        símismo.proveedor_meteo = None
        símismo.modelo = símismo._gen_modelo()
        f_0_pcse = símismo.modelo.agromanager.start_date
        f_0_tkn = símismo.sim.sim.simul_exper.t.fecha
        if f_0_pcse < f_0_tkn:
            raise ValueError(
                "Simulación PCSE empieza el {f_pcse}, pero la simulación de Tiko'n empieza el {f_tkn}.".format(
                    f_pcse=format_date(f_0_pcse, locale='es'), f_tkn=format_date(f_0_tkn, locale='es')
                )
            )
        símismo.f_inic_modelo = pd.Timestamp(símismo.modelo.agromanager.start_date)

    @property
    def org(símismo):
        pp = símismo.modelo.parameterprovider
        try:
            cultivo = pp.current_crop_name
            variedad = pp.current_variety_name
        except AttributeError:
            texto = pp['CRPNAM'].lower()
            cultivo = next(clt for clt in símismo.sim.trads_cultivos if texto.startswith(clt.lower()))
            variedad = texto[len(cultivo):].strip() or None

        return símismo.sim.obt_org(cultivo=cultivo, variedad=variedad)

    def _gen_modelo(símismo):
        return símismo.sim.parcelas.gen_modelo_pcse(símismo.proveedor_meteo)

    def _gen_proveedor_meteo(símismo):
        parc = str(símismo.sim.parcelas.parcelas[0])
        centr = símismo.sim.sim.exper.controles['centroides'].loc[{EJE_PARC: parc}]
        lat, lon = centr.loc[{EJE_COORD: 'lat'}].matr[0, 0], centr.loc[{EJE_COORD: 'lon'}].matr[0, 0]
        elev = símismo.sim.sim.exper.controles['elevaciones'].loc[{EJE_PARC: parc}].matr[0]

        clima = símismo.sim.sim.clima
        bd_pandas = clima.datos.loc[{EJE_PARC: parc}].drop_vars(EJE_PARC).to_dataframe()
        return ProveedorMeteoPCSEPandas(bd_pandas, lat=lat, lon=lon, elev=elev)

    def iniciar(símismo):
        if not símismo.proveedor_meteo:
            símismo.proveedor_meteo = símismo._gen_proveedor_meteo()
        símismo.modelo = símismo._gen_modelo()
        símismo.llenar_vals()

    def incrementar(símismo, paso, f):
        if f > símismo.f_inic_modelo:
            símismo.modelo.run(paso)
        if símismo.modelo.flag_terminate:
            avisar("Modelo PCSE terminó simulación antes de la simulación completa de Tiko'n.")
        símismo.llenar_vals()

    def llenar_vals(símismo):
        org = símismo.org
        for vr, (vr_pcse, conv) in símismo._conv_vars.items():
            val = símismo.modelo.get_variable(vr_pcse)
            if val is not None:
                símismo.datos[RES_BIOMASA].loc[{EJE_ETAPA: org[vr]}] = val * conv

        símismo.datos[RES_HUMSUELO][:] = símismo.modelo.get_variable('SM')

    def aplicar_daño(símismo, daño):
        org = símismo.org
        daño = daño.renombrar({EJE_VÍCTIMA: EJE_ETAPA})
        etapas_activas = [etp for etp in daño.coords[EJE_ETAPA] if etp.org is org]
        for etp in etapas_activas:
            try:
                var, conv = símismo._conv_vars[etp.nombre]
            except KeyError:
                continue
            val = símismo.modelo.get_variable(var)
            if val is not None:
                símismo.modelo.set_variable(var, val - daño.loc[{EJE_ETAPA: etp}].matr.item() / conv)

    def cerrar(símismo):
        pass


class SimulPCSE(SimulCultivoExterno):
    cls_instancia = InstanciaPCSE
    trads_cultivos = {
        'barley': 'cebada',
        'cassava': 'mandioca',
        'chickpea': 'garbanzo',
        'cotton': 'algodón',
        'cowpea': 'frijol de carita',
        'fababean': 'haba',
        'groundnut': 'maní',
        'maize': 'maíz',
        'millet': 'mijo',
        'mungbean': 'mungo',
        'pigeonpea': 'guandú',
        'potato': 'papa',
        'rapeseed': 'raps',
        'rice': 'arroz',
        'sorghum': 'sorgo',
        'soybean': 'soya',
        'sugar beet': 'remolacha azucarera',
        'sugarcane': 'caña',
        'sunflower': 'girasol',
        'sweetpotato': 'batata',
        'tobacco': 'tabaco',
        'winter wheat': 'trigo de invierno',
        'wheat': 'trigo'
    }

    def requísitos(símismo, controles=False):
        if not controles:
            return {'clima.temp_máx', 'clima.temp_mín', 'clima.rad_solar', 'clima.precip'}
