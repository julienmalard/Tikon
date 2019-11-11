import datetime
import socket
import subprocess
from warnings import warn as avisar

import numpy as np
import pandas as pd
from tikon.móds.cultivo.extrn import SimulCultivoExterno, InstanciaSimulCultivo
from tikon.móds.cultivo.res import RES_HUMSUELO, RES_BIOMASA
from tikon.móds.rae.red.utils import EJE_ETAPA
from tikon.result import EJE_COORD, EJE_PARC


class InstanciaDSSAT(InstanciaSimulCultivo):

    def __init__(símismo, sim, vars_, índs):
        super().__init__(sim, vars_, índs)

        f_inic = sim.mnjdr.get_value('SDATE')
        símismo.f_inic_modelo = pd.Timestamp(datetime.datetime.strptime(f_inic, '%Y%j').date())

        parc = str(sim.parcelas[0])
        clima = símismo.sim.sim.clima
        bd_pandas = clima.datos.loc[{EJE_PARC: parc}].drop(EJE_PARC).to_dataframe()

    def _gen_modelo(símismo):
        símismo.proceso = ProcesoDSSAT()

    def incrementar(símismo, paso, f):
        if f > símismo.f_inic_modelo:
            símismo.modelo.run(paso)
        if símismo.modelo.flag_terminate:
            avisar("Modelo PCSE terminó simulación antes de la simulación completa de Tiko'n.")
        símismo.llenar_vals()

    def cerrar(símismo, paso, f):
        pass


class ProcesoDSSAT(object):
    def __init__(símismo):
        símismo.enchufe = socket
        subprocess.Popen(
            [símismo.comanda, '-p', ],
            cwd=símismo.dir
        )
        símismo.comanda = os.path.join(ctrl.dir_DSSAT, comanda) + " B " + símismo.dir + "DSSBatch.v46"


class SimulDSSAT(SimulCultivoExterno):
    cls_instancia = InstanciaDSSAT
    _trads_cultivos = {
        'AL': 'alfalfa',
        'BA': 'cebada',
        'BH': 'pasto bahía',
        'BM': 'grama común',
        'BN': 'frijol',
        'BR': 'brachiaria',
        'BS': 'remolacha azucarera',
        'CB': 'repollo',
        'CH': 'garbanzo',
        'CN': 'canola',
        'CO': 'algodón',
        'CP': 'frijol de carita',
        'CS': 'mandioca',
        'FB': 'haba',
        'GB': 'judía verde',
        'ML': 'mijo',
        'MZ': 'maíz',
        'PI': 'piña',
        'PN': 'maní',
        'PP': 'guandú',
        'PR': 'pimiento',
        'PT': 'papa',
        'RI': 'arroz',
        'SB': 'soya',
        'SC': 'caña',
        'SF': 'cártamo',
        'SG': 'sorgo',
        'SU': 'girasol',
        'SW': 'maíz dulce',
        'TM': 'tomate',
        'TN': 'taro',
        'VB': 'frijol terciopelo',
        'WH': 'trigo',
    }

    def requísitos(símismo, controles=False):
        if not controles:
            return {'clima.temp_máx', 'clima.temp_mín', 'clima.rad', 'clima.precip'}


class InstanciaPCSE(InstanciaSimulCultivo):
    _conv_vars = {
        'hojas': ('LAI', 1),
        'raíces': ('WRT', 1 / 10000),
        'palo': ('WST', 1 / 10000),
        'fruta': ('WSO', 1 / 10000)
    }

    def __init__(símismo, sim, índs):
        super().__init__(sim=sim, vars_=[RES_HUMSUELO, RES_BIOMASA], índs=índs)
        parc = str(sim.parcelas[0])
        centr = símismo.sim.sim.simul_exper.controles['centroides'].loc[{EJE_PARC: parc}]
        lat, lon = centr.loc[{EJE_COORD: 'lat'}], centr.loc[{EJE_COORD: 'lon'}]
        elev = símismo.sim.sim.simul_exper.controles['elevaciones'].loc[{EJE_PARC: parc}]

        clima = símismo.sim.sim.clima

        símismo._proveedor_meteo = ProveedorMeteoPCSEPandas(bd_pandas, lat=lat, lon=lon, elev=elev)

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


mods_cult = {
    'Maíz': {
        'DSSAT': {
            'IXIM': {
                'Comanda': '{exe_DSSAT} MZIXM046'.format(**dic_info),
                'Código cultivo': 'MZ'
            },
            'CERES': {
                'Comanda': '{exe_DSSAT} MZCER046'.format(**dic_info),
                'Código cultivo': 'MZ'
            }
        }
    },
    'Tomate': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': '{exe_DSSAT} CRGRO046'.format(**dic_info),
                'Código cultivo': 'TM'
            }
        }
    },
    'Frijol': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': '{exe_DSSAT} CRGRO046'.format(**dic_info),
                'Código cultivo': 'BN'
            }
        }
    },
    'Repollo': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': '{exe_DSSAT} CRGRO046'.format(**dic_info),
                'Código cultivo': 'CB'
            }
        }
    },
    'Papas': {
        'DSSAT': {
            'SUBSTOR': {
                'Comanda': '{exe_DSSAT} PTSUB046'.format(**dic_info),
                'Código cultivo': 'PT'
            }
        }
    },
    'Piña': {
        'PIAL': {
            'CROPGRO': {
                'Comanda': 'MDRIV980.EXE MINPT980.EXE PIALO980.EXE I',
                'Código cultivo': 'PI'
            }
        }
    },
    'Habas': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': '{exe_DSSAT} CRGRO046'.format(**dic_info),
                'Código cultivo': 'FB'
            }
        }
    },
    'Garbanzo': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': '{exe_DSSAT} CRGRO046'.format(**dic_info),
                'Código cultivo': 'CH'
            }
        }
    }
}
