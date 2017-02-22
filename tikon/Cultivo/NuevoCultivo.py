import numpy as np
import os
import subprocess

from tikon.Coso import Simulable
from tikon.Cultivo import Controles as ctrl
from tikon.Cultivo.ModExtern.DSSAT import DSSAT


class Cultivo(Simulable):
    """
    Esta clase sirve para representar cultivos agrícolas.
    """

    # La extension para guardar archivos de cultivos.
    ext = '.clt'

    def __init__(símismo, cultivo, variedad, programa=None, cód_modelo=None):
        super().__init__(nombre=variedad)

        símismo.cultivo = cultivo
        símismo.variedad = variedad

        símismo.programa = None
        símismo.cód_modelo = None

        símismo.modelo = np.array([], dtype=object)

    def estab_modelo(símismo, programa, cód_modelo, dir_trabajo):
        """

        :param programa:
        :type programa: str

        :param cód_modelo:
        :type cód_modelo: str

        :param dir_trabajo:
        :type dir_trabajo: str

        :return:
        :rtype: EnvolturaModCult
        """

        símismo.programa = programa
        símismo.cód_modelo = cód_modelo

        if programa is None:
            programa = list(sorted(mods_cult[símismo.cultivo]))[0]
        if cód_modelo is None:
            cód_modelo = list(sorted(mods_cult[símismo.cultivo][programa]))[0]

        if programa == 'DSSAT':
            modelo = EnvolturaDSSAT(cultivo=símismo.cultivo, variedad=símismo.variedad,
                                    cód_mod=cód_modelo,
                                    dir_trabajo=dir_trabajo)
        elif programa == 'CropSyst':
            raise ValueError('Marcela, ¡este es para ti! Haz CLIC en este error y ya puedes empezar a codigar. :)')
        else:
            raise ValueError('Falta implementar el modelo "{}" en Tiko\'n.'.format(programa))

        return modelo

    def dibujar(símismo, mostrar=True, archivo=None, exper=None, **kwargs):
        raise NotImplementedError  # Para hacer

    def _prep_obs_exper(símismo, exper):
        raise NotImplementedError  # Para hacer

    def _procesar_predics_calib(símismo):
        raise NotImplementedError  # Para hacer

    def incrementar(símismo, paso, i, extrn):
        raise NotImplementedError  # Para hacer

    def _sacar_líms_coefs_interno(símismo):
        raise NotImplementedError  # Para hacer

    def _llenar_coefs(símismo, n_rep_parám, calibs, comunes, usar_especificadas):
        raise NotImplementedError  # Para hacer

    def _procesar_validación(símismo):
        raise NotImplementedError  # Para hacer

    def _prep_args_simul_exps(símismo, exper, n_rep_estoc, n_rep_paráms, **kwargs):
        raise NotImplementedError  # Para hacer

    def _actualizar_vínculos_exps(símismo):
        raise NotImplementedError  # Para hacer

    def _sacar_coefs_interno(símismo):
        raise NotImplementedError  # Para hacer


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

    def prep_simul(símismo, info_simul):
        """

        :param info_simul:
        :type info_simul: dict

        """
        raise NotImplementedError

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

    def leer_resultados(símismo):
        raise NotImplementedError


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

    def leer_resultados(símismo):
        resul = DSSAT.leer_egr(directorio=símismo.dir)




# Para hacer: cambiar los códigos de los ejecutables a los modificados para intercambiar info de plagas

mods_cult = {
    'Maíz': {
        'DSSAT': {
            'IXIM': {
                'Comanda': 'DSCSM046.EXE MZIXM046',
                'Código cultivo': 'MZ'
            },
            'CERES': {
                'Comanda': 'DSCSM046.EXE MZCER046',
                'Código cultivo': 'MZ'
            }
        }
    },
    'Tomate': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': 'DSCSM046.EXE CRGRO046',
                'Código cultivo': 'TM'
            }
        }
    },
    'Frijol': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': 'DSCSM046.EXE CRGRO046',
                'Código cultivo': 'BN'
            }
        }
    },
    'Repollo': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': 'DSCSM046.EXE CRGRO046',
                'Código cultivo': 'CB'
            }
        }
    },
    'Papas': {
        'DSSAT': {
            'SUBSTOR': {
                'Comanda': 'DSCSM046.EXE PTSUB046',
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
                'Comanda': 'DSCSM046.EXE CRGRO046',
                'Código cultivo': 'FB'
            }
        }
    },
    'Garbanzo': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': 'DSCSM046.EXE CRGRO046',
                'Código cultivo': 'CH'
            }
        }
    }
}
