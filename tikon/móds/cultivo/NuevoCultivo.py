import os
import subprocess

from tikon0.Cultivo.ModExtern.DSSAT import DSSAT

from tikon0.Cultivo import Controles as ctrl

dirs_auto = {
    'DSSAT': "C:\\DSSAT46",
}


class EnvolturaModCult(object):

    def __init__(símismo, cultivo, variedad, dir_trabajo):

        símismo.cultivo = cultivo
        símismo.variedad = variedad

        símismo.dir = os.path.join(dir_trabajo, "Tiko'n_Docs_mod_cult")

        # El diccionario con los valores de egreso
        símismo.egresos = {
            "raices": None, "hojas": None, "asim": None, "tallo": None, "semillas": None, "frutas": {},
            "nubes": None, "humrel": None, "lluvia": None, "tprom": None, "tmin": None, "tmax": None, "radsol": None,
            "tsuelo": None, "humsuelo": None
        }

        símismo.comanda = NotImplemented

        símismo.proceso = None

    def empezar_simul(símismo):

        símismo.proceso = subprocess.Popen(
            símismo.comanda,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            cwd=símismo.dir,
            universal_newlines=True
        )

    def incrementar(símismo, paso, daño_plagas=None):
        """

        :param paso:
        :type paso: int


        :param daño_plagas:
        :type daño_plagas: dict

        """

        # Convertir el diccionario de daño de plagas al formato texto (para ingresar en la línea de comanda)
        # El diccionario debe tener el formato siguiente: daño_plagas = dict(daño_hojas = (), daño_raíces = (),
        # daño_tallo = (), daño_semillas = (), daño_frutas = (), daño_asim = ()}
        if daño_plagas is None:
            tx_daño_plagas = ''
        else:
            tx_daño_plagas = ''.join(['{}: {};'.format(nmb, dñ) for nmb, dñ in daño_plagas.items()])

        # Para compatibilidad con FORTRAN (el modelo de cultivos DSSAT) y probablemente C++ también:
        conv_utf = [("ñ", "n"), ("í", "i"), ('é', 'e'), ('á', 'a'), ('ó', 'o'), ('ú', 'u'), ('Á', 'A'), ('É', 'E'),
                    ('Í', 'I'), ('Ó', 'O'), ('Ú', 'U')]
        for c in conv_utf:
            tx_daño_plagas.replace(c[0], c[1])

        # Agregar el paso
        tx = 'paso: {}:'.format(paso) + tx_daño_plagas

        símismo.proceso.stdin.write(tx)  # Envía el estado de daño al modelo de cultivo
        símismo.proceso.stdin.flush()  # Una tecnicalidad obscura
        egr = símismo.proceso.stdout.readline()

        # Los egresos llegarán en el formato siguiente:
        # raices: valor; hojas: valor; ...
        l_egr = egr.split(';')

        # Guardar los valores comunicados por el modelo externo
        for e in l_egr:
            nmb, val = e.split(': ')
            símismo.egresos[nmb] = float(val)


class EnvolturaDSSAT(EnvolturaModCult):

    def __init__(símismo, cultivo, variedad, cód_mod, dir_trabajo):
        super().__init__(cultivo=cultivo, variedad=variedad, dir_trabajo=dir_trabajo)

        comanda = mods_cult[cultivo]['DSSAT'][cód_mod]['Comanda']
        símismo.comanda = os.path.join(ctrl.dir_DSSAT, comanda) + " B " + símismo.dir + "DSSBatch.v46"

    def prep_simul(símismo, info_simul):
        """

        :param info_simul:
        :type info_simul:

        """
        DSSAT.gen_ingr(directorio=símismo.dir, cultivo=símismo.cultivo, variedad=símismo.variedad,
                       disuelo=info_simul['suelo'], meteo=info_simul['meteo'], manejo=info_simul['manejo'])


dic_info = {
    'exe_DSSAT': 'DSCSM046_TKN.EXE'
}

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
