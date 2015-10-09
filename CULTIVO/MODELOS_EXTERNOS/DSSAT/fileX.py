from CULTIVO.MODELOS_EXTERNOS.DSSAT.DSSAT import DocDssat
import os

# Objeto para representar documentos de typo FILEX de DSSAT (información de simulación)
class FileX(DocDssat):

    def __init__(simismo, dic="", *args, **kwargs):
        super().__init__(*args, **kwargs)  # Esta variable se initializa como DocDssat
        simismo.dic = dic
        if len(simismo.dic) == 0:
            simismo.dic = {"EXP.DETAILS": "",
                           "GENERAL": {"ADDRESS": [], "PEOPLE": [], "SITE": [], "PAREA": [], "PRNO": [], "PLEN": [],
                                       "PLDR": [], "PLSP": [], "PLAY": [],
                                       "HAREA": [], "HRNO": [], "HLEN": [], "HARM": [], "NOTES": []
                                       },
                           "CULTIVARS": {"CR": [], "INGENO": [], "CNAME": []},
                           "TREATMENTS": {"R": [], "O": [], "C": [], "TNAME": [], "CU": [], "FL": [], "SA": [],
                                          "IC": [], "MP": [], "MI": [], "MF": [], "MR": [], "MC": [], "MT": [],
                                          "ME": [], "MH": [], "SM": []
                                          },
                           "FIELDS": {"ID_FIELD": [], "WSTA": [], "FLSA": [], "FLOB": [], "FLDT": [], "FLDD": [],
                                      "XCRD": [], "YCRD": [], "ELEV": [], "AREA": [], "SLEN": [], "FLWR": [],
                                      "SLAS": [], "FLHST": [], "FHDUR": [], "FLDS": [], "FLST": [], "SLTX": [],
                                      "SLDP": [], "ID_SOIL": [], "FLNAME": []
                                      },
                           "SOIL ANALYSIS": {"SADAT": [], "SMHB": [], "SMPX": [], "SMKE": [], "SANAME": [], "SABL": [],
                                             "SADM": [], "SAOC": [], "SANI": [], "SAPHW": [], "SAPHB": [], "SAPX": [],
                                             "SAKE": [], "SASC": []
                                             },
                           "INITIAL CONDITIONS": {"PCR": [], "ICDAT": [], "ICRT": [], "ICND": [], "ICRN": [],
                                                  "ICRE": [], "ICWD": [], "ICRES": [], "ICREN": [], "ICREP": [],
                                                  "ICRIP": [], "ICRID": [], "ICNAME": [],
                                                  "ICBL": [[]], "SH2O": [[]], "SNH4": [[]], "SNO3": [[]]
                                                  },
                           "PLANTING DETAILS": {"PDATE": [], "EDATE": [], "PPOP": [], "PPOE": [], "PLME": [],
                                                "PLDS": [], "PLRS": [], "PLRD": [], "PLDP": [], "PLWT": [], "PAGE": [],
                                                "PENV": [], "PLPH": [], "SPRL": [], "PLNAME": []
                                                },
                           "IRRIGATION AND WATER MANAGEMENT": {"EFIR": [], "IDEP": [], "ITHR": [], "IEPT": [],
                                                               "IOFF": [], "IAME": [], "IAMT": [], "IRNAME": [],
                                                               "IDATE": [], "IROP": [], "IRVAL": []
                                                               },
                           "FERTILIZERS (INORGANIC)": {"FDATE": [], "FMCD": [], "FACD": [], "FDEP": [], "FAMN": [],
                                                       "FAMP": [], "FAMK": [], "FAMC": [], "FAMO": [], "FOCD": [],
                                                       "FERNAME": []
                                                       },
                           "RESIDUES AND ORGANIC FERTILIZER": {"RDATE": [], "RCOD": [], "RAMT": [], "RESN": [],
                                                               "RESP": [], "RESK": [], "RINP": [], "RDEP": [],
                                                               "RMET": [], "RENAME": []
                                                               },
                           "CHEMICAL APPLICATIONS": {"CDATE": [], "CHCOD": [], "CHAMT": [], "CHME": [], "CHDEP": [],
                                                     "CHT": [], "CHNAME": []
                                                     },
                           "TILLAGE": {"TL": [], "TDATE": [], "TIMPL": [], "TDEP": [], "TNAME": []},
                           "ENVIRONMENT MODIFICATIONS": {"ODATE": [], "EDAY": [], "ERAD": [], "EMAX": [], "EMIN": [],
                                                         "ERAIN": [], "ECO2": [], "EDEW": [], "EWIND": [],
                                                         "ENVNAME": []
                                                         },
                           "HARVEST DETAILS": {"HDATE": [], "HSTG": [], "HCOM": [], "HSIZE": [], "HPC": [],
                                               "HBPC": [], "HNAME": []
                                               },
                           "SIMULATION CONTROLS": {"GENERAL": [], "NYERS": [], "NREPS": [], "START": [], "SDATE": [],
                                                   "RSEED": [], "SNAME": [], "SMODEL": [],
                                                   "OPTIONS": [], "WATER": [], "NITRO": [], "SYMBI": [], "PHOSP": [],
                                                   "POTAS": [], "DISES": [], "CHEM": [], "TILL": [], "CO2": [],
                                                   "METHODS": [], "WTHER": [], "INCON": [], "LIGHT": [], "EVAPO": [],
                                                   "INFIL": [], "PHOTO": [], "HYDRO": [], "NSWIT": [], "MESOM": [],
                                                   "MESEV": [], "MESOL": [],
                                                   "MANAGEMENT": [], "PLANT": [], "IRRIG": [], "FERTI": [], "RESID": [],
                                                   "HARVS": [],
                                                   "OUTPUTS": [], "FNAME": [], "OVVEW": [], "SUMRY": [], "FROPT": [],
                                                   "GROUT": [], "CAOUT": [], "WAOUT": [], "NIOUT": [], "MIOUT": [],
                                                   "DIOUT": [], "VBOSE": [], "CHOUT": [], "OPOUT": [],
                                                   "PLANTING": [], "PFRST": [], "PLAST": [], "PH2OL": [], "PH2OU": [],
                                                   "PH2OD": [], "PSTMX": [], "PSTMN": [],
                                                   "IRRIGATION": [], "IMDEP": [], "ITHRL": [], "ITHRU": [], "IROFF": [],
                                                   "IMETH": [], "IRAMT": [], "IREFF": [],
                                                   "NITROGEN": [], "NMDEP": [], "NMTHR": [], "NAMNT": [], "NCODE": [],
                                                   "NAOFF": [],
                                                   "RESIDUES": [], "RIPCN": [], "RTIME": [], "RIDEP": [],
                                                   "HARVEST": [], "HFRST": [], "HLAST": [], "HPCNP": [], "HPCNR": []
                                                   }
                           }
            # Lista del tamaño (en carácteres) de cada variable

            simismo.prop_vars = {
                "EXP.DETAILS": {"EXP.DETAILS": 50},
                "GENERAL": {"PEOPLE": 2500, "ADDRESS": 2500, "SITE": 2500,
                            "PAREA": 5, "PRNO": 5, "PLEN": 5, "PLDR": 5, "PLSP": 5, "PLAY": 5, "HAREA": 5,
                            "HRNO": 5, "HLEN": 5, "HARM": 14,
                            "NOTES": 5000
                            },
                "CULTIVARS": {"CR": 25, "INGENO": 6, "CNAME": 16},
                "TREATMENTS": {"R": 1, "O": 1, "C": 1, "TNAME": 255, "CU": 25, "FL": 25, "SA": 25, "IC": 25, "MP": 25,
                               "MI": 25, "MF": 25, "MR": 25, "MC": 25, "MT": 25, "ME": 25, "MH": 25, "SM": 25
                               },
                "FIELDS": {"ID_FIELD": 8, "WSTA": 8, "FLSA": 5, "FLOB": 5, "FLDT": 5, "FLDD": 5, "FLDS": 5, "FLST": 5,
                           "SLTX": 5, "SLDP": 5, "ID_SOIL": 10,
                           "XCRD": 15, "YCRD": 15, "ELEV": 9, "AREA": 17, "SLEN": 5, "FLWR": 5, "SLAS": 5, "FLHST": 5,
                           "FHDUR": 5, "FLNAME": 255
                           },
                "SOIL ANALYSIS": {"SADAT": 5, "SMHB": 5, "SMPX": 5, "SMKE": 5, "SANAME": 255,
                                  "SABL": 5, "SADM": 5, "SAOC": 5, "SANI": 5, "SAPHW": 5, "SAPHB": 5, "SAPX": 5,
                                  "SAKE": 5, "SASC": 5
                                  },
                "INITIAL CONDITIONS": {"PCR": 5, "ICDAT": 5, "ICRT": 5, "ICND": 5, "ICRN": 5, "ICRE": 5, "ICWD": 5,
                                       "ICRES": 5, "ICREN": 5, "ICREP": 5, "ICRIP": 5, "ICRID": 5, "ICNAME": 255,
                                       "ICBL": 5, "SH2O": 5, "SNH4": 5, "SNO3": 5
                                       },
                "PLANTING DETAILS": {"PDATE": 5, "EDATE": 5, "PPOP": 5, "PPOE": 5, "PLME": 5, "PLDS": 5, "PLRS": 5,
                                     "PLRD": 5, "PLDP": 5, "PLWT": 5, "PAGE": 5, "PENV": 5, "PLPH": 5, "SPRL": 5,
                                     "PLNAME": 255
                                     },
                "IRRIGATION AND WATER MANAGEMENT": {"EFIR": 5, "IDEP": 5, "ITHR": 5, "IEPT": 5, "IOFF": 5, "IAME": 5,
                                                    "IAMT": 5, "IRNAME": 5, "IDATE": 5, "IROP": 5, "IRVAL": 5
                                                    },
                "FERTILIZERS (INORGANIC)": {"FDATE": 5, "FMCD": 5, "FACD": 5, "FDEP": 5, "FAMN": 5, "FAMP": 5,
                                            "FAMK": 5, "FAMC": 5, "FAMO": 5, "FOCD": 5, "FERNAME": 255
                                            },
                "RESIDUES AND ORGANIC FERTILIZER": {"RDATE": 5, "RCOD": 5, "RAMT": 5, "RESN": 5, "RESP": 5, "RESK": 5,
                                                    "RINP": 5, "RDEP": 5, "RMET": 5, "RENAME": 255
                                                    },
                "CHEMICAL APPLICATIONS": {"CDATE": 5, "CHCOD": 5, "CHAMT": 5, "CHME": 5, "CHDEP": 5, "CHT": 5,
                                          "CHNAME": 255
                                          },
                "TILLAGE": {"TL": 5, "TDATE": 5, "TIMPL": 5, "TDEP": 5, "TNAME": 255},
                "ENVIRONMENT MODIFICATIONS": {"ODATE": 5, "EDAY": 5, "ERAD": 5, "EMAX": 5, "EMIN": 5, "ERAIN": 5,
                                              "ECO2": 5, "EDEW": 5, "EWIND": 5, "ENVNAME": 255
                                              },
                "HARVEST DETAILS": {"HDATE": 5, "HSTG": 5, "HCOM": 5, "HSIZE": 5, "HPC": 5, "HBPC": 5, "HNAME": 255},
                "SIMULATION CONTROLS": {"GENERAL": 11, "NYERS": 5, "NREPS": 5, "START": 5, "SDATE": 5, "RSEED": 5,
                                        "SNAME": 255, "SMODEL": 255,
                                        "OPTIONS": 11, "WATER": 5, "NITRO": 5, "SYMBI": 5, "PHOSP": 5, "POTAS": 5,
                                        "DISES": 5, "CHEM": 5, "TILL": 5, "CO2": 5,
                                        "METHODS": 11, "WTHER": 5, "INCON": 5, "LIGHT": 5, "EVAPO": 5, "INFIL": 5,
                                        "PHOTO": 5, "HYDRO": 5, "NSWIT": 5, "MESOM": 5, "MESEV": 5, "MESOL": 5,
                                        "MANAGEMENT": 11, "PLANT": 5, "IRRIG": 5, "FERTI": 5, "RESID": 5, "HARVS": 5,
                                        "OUTPUTS": 11, "FNAME": 5, "OVVEW": 5, "SUMRY": 5, "FROPT": 5, "GROUT": 5,
                                        "CAOUT": 5, "WAOUT": 5, "NIOUT": 5, "MIOUT": 5, "DIOUT": 5, "VBOSE": 5,
                                        "CHOUT": 5, "OPOUT": 5,
                                        "PLANTING": 11, "PFRST": 5, "PLAST": 5, "PH20L": 5, "PH2OU": 5, "PH20D": 5,
                                        "PSTMX": 5, "PSTMN": 5,
                                        "IRRIGATION": 11, "IMDEP": 5, "ITHRL": 5, "ITHRU": 5, "IROFF": 5, "IMETH": 5,
                                        "IRAMT": 5, "IREFF": 5,
                                        "NITROGEN": 11, "NMDEP": 5, "NMTHR": 5, "NAMNT": 5, "NCODE": 5, "NAOFF": 5,
                                        "RESIDUES": 11, "RIPCN": 5, "RTIME": 5, "RIDEP": 5,
                                        "HARVESTS": 11, "HFRST": 5, "HLAST": 5, "HPCNP": 5, "HRCNR": 5},
            }

        # Las secciones posibles en un documento FILEX
        simismo.secciones = []
        for i in simismo.dic:
            simismo.secciones.append(i)

    # Lee un archivo FILEX para uso en Python. "Documento" es la ubicación del archivo FILEX en la computadora.
    def leer(simismo, documento):
        # Borar datos, si existen
        for i in simismo.dic:
            for j in simismo.dic[i]:
                simismo.dic[i][j] = []

        with open(documento, "r") as d:
            doc = []
            for línea in d:
                doc.append(línea)

        # Leer todas las secciones
        for núm_lín, línea in enumerate(doc):

            # Sección "EXP.DETAILS"
            if "*EXP.DETAILS" in línea:
                simismo.dic["EXP.DETAILS"] = línea.replace("*EXP.DETAILS: ", "").replace('\n', '')
                continue

            # Sección "GENERAL"
            if '@' in línea and 'PEOPLE' in línea:
                simismo.dic["PEOPLE"] = [doc[núm_lín + 1].replace('\n', '')]
                continue  # Pasa a la línea siguiente del documento
            if '@' in línea and 'ADDRESS' in línea:
                simismo.dic["ADDRESS"] = [doc[núm_lín + 1].replace('\n', '')]
                continue  # Pasa a la línea siguiente del documento
            if '@' in línea and 'SITE(S)' in línea:
                simismo.dic["SITE"] = [doc[núm_lín + 1].replace('\n', '')]
                continue  # Pasa a la línea siguiente del documento
            vars_parcela = "PAREA  PRNO  PLEN  PLDR  PLSP  PLAY HAREA  HRNO  HLEN  HARM".split()
            if '@' in línea and 'PAREA' in línea:
                valores_parcela = doc[
                    doc.index("@ PAREA  PRNO  PLEN  PLDR  PLSP  PLAY HAREA  HRNO  HLEN  HARM.........\n")+1
                ].split()
                for a in simismo.dic['GENERAL']:
                    simismo.dic['GENERAL'][a] = [valores_parcela[vars_parcela.index(a)]]
                continue
            if '@' in línea and 'NOTES' in línea:
                notas = ""
                i = núm_lín
                while "*TREATMENTS" not in doc[núm_lín]:
                    notas += doc[i]
                    i += 1
                simismo.dic["NOTES"] = [notas]
                continue

            # Leer las secciones aparte la "GENERAL" y la "EXP.DETAILS"
            for otra in simismo.secciones:
                if otra != "EXP.DETAILS" and otra != "GENERAL":
                    simismo.decodar(doc, otra)

    def escribir(simismo, carpeta):      # Escribe un documento FILEX para uso en DSSAT
        documento = os.path.join(carpeta, 'TKON0000')  # Sólo podemos tener un documento FILEX por carpeta (parcela)
        for i in simismo.dic:    # Llenar variables vacíos con -99 (el código de DSSAT para datos que faltan)
            if type(simismo.dic[i]) is dict:
                for j in simismo.dic[i]:
                    if not len(simismo.dic[i][j]):
                        simismo.dic[i][j] = [["-99"]]
            else:
                if simismo.dic[i] == '':
                    simismo.dic[i] = [["-99"]]
        with open("FILEX.txt", "r") as d:    # Abrir el patrón general para archivos FILEX
            doc = []
            for línea in d:
                doc.append(línea)
            doc.append("\n")  # Terminar con una línea vacía para marcar el fin del documento

        # Encodar todas las secciones
        for sección in simismo.secciones:
            simismo.encodar(doc, sección)

        # Salvar la carpeta FILEX en la ubicación contenida en "documento"
        with open(documento, "w") as d:
            d.write(''.join(doc))

    # Esta funcción convierte una sección de un documento FILEX en una parte del diccionario Python del objeto fileX
    def decodar(simismo, doc, sección):
        # Encuentra la ubicación del principio y del fin de cada sección
        prin = fin = None
        for línea in doc:
            if "*" in línea and sección in línea:
                prin = doc.index(línea)
                fin = doc.index("\n", prin)
                break

        if prin:  # Si existe la sección
            for línea, texto in enumerate(doc[prin:fin-1], start=prin):
                if "@" in texto and 'AUTOMATIC MANAGEMENT' not in texto:
                    variables = texto.split()[1:]
                    for a, var in enumerate(variables):
                        if '.' in var:  # Para el caso donde variables en FILEX estén separados por '.' y no por ' '
                            variable = variables[a].split('.')
                            variable.reverse()  # Una acrobacia informática para poner las cosas en orden
                            for b in variable:
                                if len(b):
                                    variables.insert(a, b)
                            variables.remove(var)  # Terminado la acrobacia
                    i = línea+1
                    while "@" not in doc[i] and doc[i] != '\n':
                        valores = doc[i].replace('\n', '')[2:]
                        nivel = doc[i].split()[0]
                        if not nivel.isdigit():
                            nivel = 1
                        else:
                            nivel = int(nivel)

                        for j, var in enumerate(variables):
                            if var in simismo.dic[sección]:  # Si la variable existe en la base de datos de fileX
                                if len(simismo.dic[sección][var]) < nivel:
                                    simismo.dic[sección][var].append([])
                                simismo.dic[sección][var][nivel-1].append(
                                    valores[:simismo.prop_vars[sección][var]+1].strip()
                                )
                                valores = valores[simismo.prop_vars[sección][var]+1:]
                        i += 1
        else:
            return "No encontramos la sección " + sección + ". Si no eres un programador de Tikon, dígale " \
                                                            "a uno que se ponga a trabajar."

    # Esta funcción encoda una sección del diccionario en un formato de documento FILEX
    def encodar(self, doc, sección):
        prin = 0
        while '*' not in doc[prin] and sección not in doc[prin]:    # Encontrar el principio de la sección
            prin += 1
        línea = prin

        while línea != doc.index("\n", prin):  # Mientras no llegamos al fin de la sección
            línea += 1
            texto = doc[línea]
            if sección == "EXP.DETAILS":
                texto.format(**self.dic)
                doc.insert(línea, texto)
                return
            if '{' in texto:   # Si la línea tiene variables a llenar
                # Leer el primer variable de la línea (para calcular el número de niveles y repeticiones más adelante)
                var = texto[texto.index("{")+2:texto.index("]")]
                copia = texto   # Copiar la línea vacía (en caso que hayan otras líneas que agregar)
                for i, a in enumerate(self.dic[sección][var]):    # Para cada nivel de tratamiento
                    # Para cada repetición del nivel (por ej., varias aplicaciones de riego al mismo tratamiento)
                    for j, b in enumerate(a):
                        if sección != "GENERAL":
                            texto = " " + str(i + 1) + copia  # Escribir el nivel del tratamiento
                        texto = texto.replace("]", "][" + str(i) + "][" + str(j) + "]").replace(
                            "{[", "{" + sección + "[")
                        texto = texto.format(**self.dic)
                        doc.insert(línea, texto)
                        línea += 1
                doc.remove(copia)

# # Pruebas:
# prueba = Files()
# prueba.leer('IB00000002')
# prueba.escribir('IB00000002')
# # prueba = filex()
# # prueba.leer('C:\DSSAT45\Maize\BRPI0202.MZX')
# # prueba.escribir('C:\DSSAT45\Maize\BRPI0202_PRUEBA.MZX')
