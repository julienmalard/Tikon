from warnings import warn as avisar

import numpy as np
import pandas as pd
from tikon.móds.cultivo.extrn import SimulCultivoExterno, InstanciaSimulCultivo
from tikon.móds.cultivo.res import RES_HUMSUELO, RES_BIOMASA
from tikon.móds.rae.red.utils import EJE_ETAPA

from .meteo import ProveedorMeteoPCSEPandas


class InstanciaPCSE(InstanciaSimulCultivo):
    _conv_vars = {
        'hojas': ('LAI', 1),
        'raíces': ('WRT', 1 / 10000),
        'palo': ('WST', 1 / 10000),
        'fruta': ('WSO', 1 / 10000)
    }

    def __init__(símismo, sim, índs):
        super().__init__(sim=sim, vars_=[RES_HUMSUELO, RES_BIOMASA], índs=índs)
        símismo.f_inic_modelo = pd.Timestamp(símismo.modelo.agromanager.start_date)

        clima = símismo.sim.sim.clima
        símismo._proveedor_meteo = ProveedorMeteoPCSEPandas(clima.bd_total)

        símismo.modelo = símismo._gen_modelo()

    @property
    def org(símismo):
        pp = símismo.modelo.parameterprovider
        try:
            cultivo = pp.current_crop_name
            variedad = pp.current_variety_name
        except AttributeError:
            cultivo = pp['CRPNAM']
            variedad = None

        return símismo.sim.obt_org(cultivo=cultivo, variedad=variedad)

    def _gen_modelo(símismo):
        return símismo.sim.parcelas.gen_modelo_pcse(símismo._proveedor_meteo)

    def iniciar(símismo):
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
            val = símismo.modelo.get_variable(vr_pcse) * conv
            símismo.datos[RES_BIOMASA].loc[{EJE_ETAPA: org[vr]}] = val if val is not None else np.nan

        símismo.datos[RES_HUMSUELO][:] = símismo.modelo.get_variable('SM')

    def aplicar_daño(símismo, daño):
        org = símismo.org
        etapas_activas = [etp for etp in daño[EJE_ETAPA] if etp.org is org]
        for etp in etapas_activas:
            try:
                var, conv = símismo._conv_vars[etp.nombre]
            except KeyError:
                continue
            símismo.modelo.set_variable(var, daño.loc[{EJE_ETAPA: etp}] / conv)

    def cerrar(símismo, paso, f):
        pass


class SimulPCSE(SimulCultivoExterno):
    cls_instancia = InstanciaPCSE
    _trads_cultivos = {
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
        'sugarbeet': 'remolacha azucarera',
        'sugarcane': 'caña',
        'sunflower': 'girasol',
        'sweetpotato': 'batata',
        'tobacco': 'tabaco',
        'wheat': 'trigo'
    }

    def __init__(símismo, sim, parcelas):
        super().__init__(sim=sim, parcelas=parcelas)

    def obt_org(símismo, cultivo, variedad=None):
        try:
            cultivo = símismo._trads_cultivos[cultivo.lower()]
        except KeyError:
            pass
        super().obt_org(cultivo, variedad)

    def requísitos(símismo, controles=False):
        if not controles:
            return {'clima.temp_máx', 'clima.temp_mín', 'clima.rad', 'clima.precip'}
