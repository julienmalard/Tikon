import os
from CULTIVO.DSSAT.fileX import Filex
from CULTIVO.DSSAT.fileS import FileS
from CULTIVO.DSSAT.fileW import FileW
from CULTIVO.DSSAT.fileC import FileC

# Objeto general para representar documentos de DSSAT (suelos, variedades, experimentos, etc.)
class DocDssat(object):
    def __init__(simismo):
        simismo.dir_DSSAT = "C:\DSSAT46"

    def gen_ingresos(nombre="", fecha_init="", carpeta="", cultivo="", modelo="", variedad="", suelo="", meteo=""):
        # Leer las carpetas con la información de conversión de variables Tikon-DSSAT
        conv_var_suelos = {}
        with open(os.path.join(os.getcwd(), "CULTIVO\Variables_suelos.csv")) as d:
                for núm_línea, línea in enumerate(d):
                    if núm_línea == 0:
                        # La columna para los variables de DSSAT
                        col_DSSAT = línea.replace("\n", "").split(';').index("DSSAT")
                    else:
                        datos = línea.replace("\n", "").split(';')
                        variable = datos[0]
                        var_DSSAT = datos[col_DSSAT]
                        conv_var_suelos[variable] = {}
                        conv_var_suelos[variable]["DSSAT"] = var_DSSAT
        conv_var_variedades = {}
        with open(os.path.join(os.getcwd(), "CULTIVO\Variables_variedades.csv")) as d:
                for núm_línea, línea in enumerate(d):
                    if núm_línea == 0:
                        # La columna para los variables de DSSAT
                        col_DSSAT = línea.replace("\n", "").split(';').index("DSSAT")
                    else:
                        datos = línea.replace("\n", "").split(';')
                        variable = datos[0]
                        var_DSSAT = datos[col_DSSAT]
                        conv_var_variedades[variable] = {}
                        conv_var_variedades[variable]["DSSAT"] = var_DSSAT
        # Crear un objeto de carpeta de suelos DSSAT para manejar los datos
        files = FileS()
        for var in suelo.dic:
            if var in conv_var_suelos.keys():
                files.dic[conv_var_suelos[var]["DSSAT"]] = suelo.dic[var]
        files.escribir(cod_suelo=nombre)

        # Crear un objeto de carpeta de variedades DSSAT para manejar los datos
        filec = FileC(nombre=nombre, cultivo=cultivo, modelo=modelo)
        for var in variedad.dic:
            if var in conv_var_variedades.keys():
                filec.dic[conv_var_variedades[var]["DSSAT"]] = variedad.dic[var]
        filec.escribir()

#     # Crear un objeto de carpeta de ingreso DSSAT para manejar los datos
#     filex = Filex()
#     filex.dic[]
#     filex.dic["GENERAL"] =
#     filex.dic["CULTIVARS"] =
#     filex.dic["TREATMENTS"] =
#     filex.dic["FIELDS"] =
#     filex.dic["PLANTING DETAILS"] =
#     filex.dic["IRRIGATION AND WATER MANAGEMENT"] =
#     filex.dic["FERTILIZERS (INORGANIC)"] =
#     filex.dic["RESIDUES AND ORGANIC FERTILIZER"] =
#     filex.dic["TILLAGE"] =
#     filex.dic["HARVEST DETAILS"] =
#     filex.dic["SIMULATION CONTROLS"] =
#     filex.escribir()
#
#
# "EXP.DETAILS": "",
#              "GENERAL": {"ADDRESS": [], "PEOPLE": [], "SITE": [], "PAREA": [], "PRNO": [], "PLEN": [], "PLDR": [], "PLSP": [], "PLAY": [],
#                          "HAREA": [], "HRNO": [], "HLEN": [], "HARM": [], "NOTES": []},
#              "CULTIVARS": {"CR": [], "INGENO": [], "CNAME": []},
#              "TREATMENTS": {"R": [], "O": [], "C": [], "TNAME": [], "CU": [], "FL": [], "SA": [], "IC": [], "MP": [],
#                             "MI": [], "MF": [], "MR": [], "MC": [], "MT": [], "ME": [], "MH": [], "SM": []},
#              "FIELDS": {"ID_FIELD": [], "WSTA": [], "FLSA": [], "FLOB": [], "FLDT": [], "FLDD": [],
#                         "XCRD": [], "YCRD": [], "ELEV": [], "AREA": [], "SLEN": [], "FLWR": [], "SLAS": [],
#                         "FLHST": [], "FHDUR": [], "FLDS": [], "FLST": [], "SLTX": [], "SLDP": [], "ID_SOIL": [], "FLNAME": []},
#              "PLANTING DETAILS": {"PDATE": [], "EDATE": [], "PPOP": [], "PPOE": [], "PLME": [], "PLDS": [],
#                                   "PLRS": [], "PLRD": [], "PLDP": [], "PLWT": [], "PAGE": [], "PENV": [],
#                                   "PLPH": [], "SPRL": [], "PLNAME": []},
#              "IRRIGATION AND WATER MANAGEMENT": {"EFIR": [], "IDEP": [], "ITHR": [], "IEPT": [],
#                                                  "IOFF": [], "IAME": [], "IAMT": [], "IRNAME": [],
#                                                  "IDATE": [], "IROP": [], "IRVAL": [], "EFIR": [],},
#              "FERTILIZERS (INORGANIC)": {"FDATE": [], "FMCD": [], "FACD": [], "FDEP": [], "FAMN": [], "FAMP": [],
#                                          "FAMK": [], "FAMC": [], "FAMO": [], "FOCD": [], "FERNAME": []},
#              "RESIDUES AND ORGANIC FERTILIZER": {"RDATE": [], "RCOD": [], "RAMT": [], "RESN": [], "RESP": [],
#                                                  "RESK": [], "RINP": [], "RDEP": [], "RMET": [], "RENAME": []},
#              "CHEMICAL APPLICATIONS": {"CDATE": [], "CHCOD": [], "CHAMT": [], "CHME": [], "CHDEP": [], "CHT": [], "CHNAME": []},
#              "TILLAGE": {"TL": [], "TDATE": [], "TIMPL": [], "TDEP": [], "TNAME": []},
#              "ENVIRONMENT MODIFICATIONS": {"ODATE": [], "EDAY": [], "ERAD": [], "EMAX": [], "EMIN": [], "ERAIN": [],
#                                            "ECO2": [], "EDEW": [], "EWIND": [], "ENVNAME": []},
#              "HARVEST DETAILS": {"HDATE": [], "HSTG": [], "HCOM": [], "HSIZE": [], "HPC": [],
#                                  "HBPC": [], "HNAME": []},
#              "SIMULATION CONTROLS": {"GENERAL": [], "NYERS": [], "NREPS": [], "START": [], "SDATE": [], "RSEED": [], "SNAME": [], "SMODEL": [],
#                                      "OPTIONS": [], "WATER": [], "NITRO": [], "SYMBI": [], "PHOSP": [], "POTAS": [], "DISES": [], "CHEM": [], "TILL": [], "CO2": [],
#                                      "METHODS": [], "WTHER": [], "INCON": [], "LIGHT": [], "EVAPO": [], "INFIL": [], "PHOTO": [], "HYDRO": [], "NSWIT": [], "MESOM": [], "MESEV": [], "MESOL": [],
#                                      "MANAGEMENT": [], "PLANT": [], "IRRIG": [], "FERTI": [], "RESID": [], "HARVS": [],
#                                      "OUTPUTS": [], "FNAME": [], "OVVEW": [], "SUMRY": [], "FROPT": [], "GROUT": [], "CAOUT": [], "WAOUT": [], "NIOUT": [], "MIOUT": [], "DIOUT": [], "VBOSE": [], "CHOUT": [], "OPOUT": [],
#                                      "PLANTING": [], "PFRST": [], "PLAST": [], "PH2OL": [], "PH2OU": [], "PH2OD": [], "PSTMX": [], "PSTMN": [],
#                                      "IRRIGATION": [], "IMDEP": [], "ITHRL": [], "ITHRU": [], "IROFF": [], "IMETH": [], "IRAMT": [], "IREFF": [],
#                                      "NITROGEN": [], "NMDEP": [], "NMTHR": [], "NAMNT": [], "NCODE": [], "NAOFF": [],
#                                      "RESIDUES": [], "RIPCN": [], "RTIME": [], "RIDEP": [],
#                                      "HARVEST": [], "HFRST": [], "HLAST": [], "HPCNP": [], "HPCNR": []}

#