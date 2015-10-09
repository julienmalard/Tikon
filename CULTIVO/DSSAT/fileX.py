import os


#Lista del tamaño (en carácteres) de cada variable
prop_vars = {"PEOPLE": 2500, "ADDRESS": 2500, "SITE": 2500, "NOTES": 5000,
             "PAREA": 5, "PRNO": 5, "PLEN": 5, "PLDR": 5, "PLSP": 5, "PLAY": 5, "HAREA": 5, "HRNO": 5, "HLEN": 5, "HARM": 14,
             "R": 1, "O": 1, "C": 1, "TNAME": 255, "CU": 25, "FL": 25, "SA": 25, "IC": 25, "MP": 25, "MI": 25, "MF": 25, "MR": 25, "MC": 25, "MT": 25, "ME": 25, "MH": 25, "SM": 25,
             "CR": 25, "INGENO":6, "CNAME": 16,
             "ID_FIELD": 8, "WSTA":8, "FLSA": 5, "FLOB": 5, "FLDT": 5, "FLDD": 5, "FLDS": 5, "FLST": 5, "SLTX": 5, "SLDP": 5, "ID_SOIL": 10, "XCRD": 15, "YCRD": 15, "ELEV":9, "AREA": 17, "SLEN": 5, "FLWR": 5, "SLAS": 5, "FLHST": 5, "FHDUR": 5, "FLNAME": 255,
             "SADAT": 5, "SMHB": 5, "SMPX": 5, "SMKE": 5, "SANAME": 255, "SABL": 5, "SADM": 5, "SAOC": 5, "SANI": 5, "SAPHW": 5, "SAPHB": 5, "SAPX": 5, "SAKE": 5, "SASC": 5,
             "PCR": 5, "ICDAT": 5, "ICRT": 5, "ICND": 5, "ICRN": 5, "ICRE": 5, "ICWD": 5, "ICRES": 5, "ICREN": 5, "ICREP": 5, "ICRIP": 5, "ICRID": 5, "ICNAME": 255, "ICBL": 5, "SH2O": 5, "SNH4": 5, "SNO3": 5,
             "PDATE": 5, "EDATE": 5, "PPOP": 5, "PPOE": 5, "PLME": 5, "PLDS": 5, "PLRS": 5, "PLRD": 5, "PLDP": 5, "PLWT": 5, "PAGE": 5, "PENV": 5, "PLPH": 5, "SPRL": 5, "PLNAME": 255,
             "EFIR": 5, "IDEP": 5, "ITHR": 5, "IEPT": 5, "IOFF": 5, "IAME": 5, "IAMT": 5, "IRNAME": 5, "IDATE": 5, "IROP": 5, "IRVAL": 5,
             "FDATE": 5, "FMCD": 5, "FACD": 5, "FDEP": 5, "FAMN": 5, "FAMP": 5, "FAMK": 5, "FAMC": 5, "FAMO": 5, "FOCD": 5, "FERNAME": 255,
             "RDATE": 5, "RCOD": 5, "RAMT": 5, "RESN": 5, "RESP": 5, "RESK": 5, "RINP": 5, "RDEP": 5, "RMET": 5, "RENAME": 255,
             "CDATE": 5, "CHCOD": 5, "CHAMT": 5, "CHME": 5, "CHDEP": 5, "CHT": 5, "CHNAME": 255,
             "TL": 5, "TDATE": 5, "TIMPL": 5, "TDEP": 5, "TNAME": 255,
             "ODATE": 5, "EDAY": 5, "ERAD": 5, "EMAX": 5, "EMIN": 5, "ERAIN": 5, "ECO2": 5, "EDEW": 5, "EWIND": 5, "ENVNAME": 255,
             "HDATE": 5, "HSTG": 5, "HCOM": 5, "HSIZE": 5, "HPC": 5, "HBPC": 5, "HNAME": 255,
             "GENERAL": 11, "NYERS": 5, "NREPS": 5, "START": 5, "SDATE": 5, "RSEED": 5, "SNAME": 255, "SMODEL": 255,
             "OPTIONS": 11, "WATER": 5, "NITRO": 5, "SYMBI": 5, "PHOSP": 5, "POTAS": 5, "DISES": 5, "CHEM": 5, "TILL": 5, "CO2": 5,
             "METHODS": 11, "WTHER": 5, "INCON": 5, "LIGHT": 5, "EVAPO": 5, "INFIL": 5, "PHOTO": 5, "HYDRO": 5, "NSWIT": 5, "MESOM": 5, "MESEV": 5, "MESOL": 5,
             "MANAGEMENT": 11, "PLANT": 5, "IRRIG": 5, "FERTI": 5, "RESID": 5, "HARVS": 5,
             "OUTPUTS": 11, "FNAME": 5, "OVVEW": 5, "SUMRY": 5, "FROPT": 5, "GROUT": 5, "CAOUT": 5, "WAOUT": 5, "NIOUT": 5, "MIOUT": 5, "DIOUT": 5, "VBOSE": 5, "CHOUT": 5, "OPOUT": 5,
             "PLANTING": 11, "PFRST": 5, "PLAST": 5, "PH20L": 5, "PH2OU": 5, "PH20D": 5, "PSTMX": 5, "PSTMN": 5,
             "IRRIGATION": 11, "IMDEP": 5, "ITHRL": 5, "ITHRU": 5, "IROFF": 5, "IMETH": 5, "IRAMT": 5, "IREFF": 5,
             "NITROGEN": 11, "NMDEP": 5, "NMTHR": 5, "NAMNT": 5, "NCODE": 5, "NAOFF": 5,
             "RESIDUES": 11, "RIPCN": 5, "RTIME": 5, "RIDEP": 5,
             "HARVESTS": 11, "HFRST": 5, "HLAST": 5, "HPCNP": 5, "HRCNR": 5,
             "ID_SOIL": 10, "SLSOURCE": 252, "SLTX": 5, "SLDP": 5, "SLDESCRIP": 50,
             "SITE": 11, "COUNTRY": 11, "LAT":8, "LONG":8, "SCS": 50,
             "SCOM": 5, "SALB": 5, "SLU1": 5, "SLDR": 5, "SLRO": 5, "SLNF": 5, "SLPF": 5, "SMHB": 5, "SMPX": 5, "SMKE": 5,
             "SLB": 5, "SLMH": 5, "SLLL": 5, "SDUL": 5, "SSAT": 5, "SRGF": 5, "SSKS": 5, "SBDM": 5,
             "SLOC": 5, "SLCL": 5, "SLSI": 5, "SLCF": 5, "SLNI": 5, "SLHW": 5, "SLHB": 5, "SCEC": 5, "SADC": 5,
             "SLPX": 5, "SLPT": 5, "SLPO": 5, "CACO3": 5, "SLAL": 5, "SLFE": 5, "SLMN": 5, "SLBS": 5, "SLPA": 5, "SLPB": 5, "SLKE": 5, "SLMG": 5, "SLNA": 5, "SLSU": 5, "SLEC": 5, "SLCA": 5}

# Objeto general para representar documentos de DSSAT (suelos, variedades, experimentos, etc.)
class DocDssat(object):
    def __init__(simismo):
        simismo.dir_DSSAT = "C:\DSSAT46"



# Objeto para representar documentos de typo FILEC de DSSAT (información de variedades de cultivos)
class Filec(DocDssat):
    def __init__(simismo, nombre, cultivo, modelo, dic={}):
        simismo.dic = dic
        simismo.nombre = nombre
        simismo.cultivo = cultivo
        simismo.modelo = modelo
        if len(simismo.dic) == 0:
            simismo.dic = {"VAR#": "", "VRNAME": simismo.nombre[0:14], "ECO#": "", "CSDL": [], "PPSEN": [], "EM-FL": [],
                        "FL-SH": [], "FL-SD": [],
                        "SD-PM": [], "FL-LF": [], "LFMAX": [], "SLAVR": [], "SIZLF": [], "XFRT": [], "WTPSD": [],
                        "SFDUR": [], "SDPDV": [], "PODUR": [], "THRSH": [], "SDPRO": [], "SDLIP": [], "MG": [],
                        "TM": [], "THVAR": [], "PL-EM": [], "EM-V1": [], "V1-JU": [], "JU-R0": [], "PM06": [],
                        "PM09": [], "LNGSH": [],"R7-R8": [], "FL-VS": [], "TRIFL": [], "RWDTH": [], "RHGHT": [],
                        "R1PPO": [], "OPTBI": [], "SLOBI": [], "P1": [], "P2": [], "P5": [], "G2": [], "G3": [],
                        "PHINT": [], "TBASE": [], "TOPT": [], "ROPT": [],
                        "P2O": [], "DJTI": [], "GDDE": [], "DSGFT": [], "RUE": [], "KCAN": [], "AX": [], "ALL": [],
                        "PEAR": [], "PSTM": [], "G2_papa": [], "G3_papa": [], "PD": [], "P2_papa": [], "TC": []}
            # El código para este cultivar
            simismo.dic["VAR#"] = "TIK" + simismo.nombre[0:2]
        # La lista de los documentos de genética de cultivos disponibles para DSSAT
        simismo.doc_cult_disp = {"MZCER046": {"Maíz": "MZCER046"},
                              "MZIXM046": {"Maíz": "MZIXM046"},
                              "CRGRO046": {"Repollo": "CBGRO046", "Frijol": "BNGRO046", "Maní": "PNGRO046",
                                           "Tomate": "TMGRO046", "Pimiento": "PRGRO046"},
                              "PTSUB046": {"Papa": "PTSUB046"}}

    def leer(self):
        # Los datos de suelos están combinados, con muchos en la misma carpeta.
        # Este programa primero verifica si se ubica el suelo en la carpeta "Python.sol".
        # Si el suelo no se ubica allá, buscará en los otros documentos de la carpeta "DSSAT45/soil/"

        documento = self.doc_cult_disp[self.modelo][self.cultivo]

        encontrado = False
        for tipo_doc in [".cul", ".eco"]:
            with open(os.path.join("C:\\DSSAT45\\Genotype",documento,tipo_doc), "r") as d:
                for línea in d:
                    if "!" in línea:
                        pass  # Saltar los comentarios
                    elif "@" in línea:
                        variables = línea.replace('.',' ').replace('@',' ').split()
                    elif self.nombre[0:14] in línea:
                        datos = línea.split()
                        for númdato, dato in enumerate(datos):
                            if variables[númdato] in self.dic.keys():
                                self.dic[variables[númdato]] = dato
                        encontrado = True
                        break
        if not encontrado:
            return "No se encontró la variedad " + self.nombre + " para el cultivo " + self.cultivo + "."

    def escribir(self):
        documento = self.doc_cult_disp[self.modelo][self.cultivo]
        for i in self.dic:    # Llenar variables vacíos con -99 (el código de DSSAT para datos que faltan)
            for j in self.dic[i]:
                if not len(self.dic[i][j]):
                    self.dic[i][j] = ["-99"]

        # Salvar la carpeta
        for tipo_doc in [".cul", ".eco"]:
            if tipo_doc == ".cul":
                with open("CROPGRO_CUL.txt", "r") as d:    # Abrir el patrón general para archivos .CUL
                    nuevo_cultivo=d.readline()
                    nuevo_cultivo += "\n"  # Terminar con una línea vacía para marcar el fin del documento
            elif tipo_doc == ".eco":
                with open("CROPGRO_ECO.txt", "r") as d:    # Abrir el patrón general para archivos .ECO
                    nuevo_cultivo=d.readline()
                    nuevo_cultivo += "\n"  # Terminar con una línea vacía para marcar el fin del documento

            nuevo_cultivo.format(**self.dic)
            print(nuevo_cultivo)
            with open(os.path.join("C:\\DSSAT45\\Genotype",documento,tipo_doc), "r+") as d:
                doc = d.readlines()
                for i,línea in enumerate(doc):
                    if self.nombre[0:14] in línea:
                        del doc[i]
                        break
                    else:
                        continue
                doc.append(nuevo_cultivo)
                d.truncate() # Borrar el documento
                d.write(''.join(doc))

# Objeto para representar documentos de typo FILEX de DSSAT (información de simulación)
class Filex(DocDssat):

    def __init__(simismo, dic={}):
        simismo.dic = dic
        if len(simismo.dic) == 0:
            dic_filex = {"EXP.DETAILS": "",
                         "GENERAL": {"ADDRESS": [], "PEOPLE": [], "SITE": [], "PAREA": [], "PRNO": [], "PLEN": [], "PLDR": [], "PLSP": [], "PLAY": [],
                                     "HAREA": [], "HRNO": [], "HLEN": [], "HARM": [], "NOTES": []},
                         "CULTIVARS": {"CR": [], "INGENO": [], "CNAME": []},
                         "TREATMENTS": {"R": [], "O": [], "C": [], "TNAME": [], "CU": [], "FL": [], "SA": [], "IC": [], "MP": [],
                                        "MI": [], "MF": [], "MR": [], "MC": [], "MT": [], "ME": [], "MH": [], "SM": []},
                         "FIELDS": {"ID_FIELD": [], "WSTA": [], "FLSA": [], "FLOB": [], "FLDT": [], "FLDD": [],
                                    "XCRD": [], "YCRD": [], "ELEV": [], "AREA": [], "SLEN": [], "FLWR": [], "SLAS": [],
                                    "FLHST": [], "FHDUR": [], "FLDS": [], "FLST": [], "SLTX": [], "SLDP": [], "ID_SOIL": [], "FLNAME": []},
                         "SOIL ANALYSIS": {"SADAT": [], "SMHB": [], "SMPX": [], "SMKE": [], "SANAME": [], "SABL": [], "SADM": [],
                                           "SAOC": [], "SANI": [], "SAPHW": [], "SAPHB": [], "SAPX": [], "SAKE": [], "SASC": []},
                         "INITIAL CONDITIONS": {"PCR": [], "ICDAT": [], "ICRT": [], "ICND": [], "ICRN": [], "ICRE": [],
                                                "ICWD": [], "ICRES": [], "ICREN": [], "ICREP": [], "ICRIP": [], "ICRID": [],
                                                "ICNAME": [], "ICBL": [[]], "SH2O": [[]], "SNH4": [[]], "SNO3": [[]]},
                         "PLANTING DETAILS": {"PDATE": [], "EDATE": [], "PPOP": [], "PPOE": [], "PLME": [], "PLDS": [],
                                              "PLRS": [], "PLRD": [], "PLDP": [], "PLWT": [], "PAGE": [], "PENV": [],
                                              "PLPH": [], "SPRL": [], "PLNAME": []},
                         "IRRIGATION AND WATER MANAGEMENT": {"EFIR": [], "IDEP": [], "ITHR": [], "IEPT": [],
                                                             "IOFF": [], "IAME": [], "IAMT": [], "IRNAME": [],
                                                             "IDATE": [], "IROP": [], "IRVAL": []},
                         "FERTILIZERS (INORGANIC)": {"FDATE": [], "FMCD": [], "FACD": [], "FDEP": [], "FAMN": [], "FAMP": [],
                                                     "FAMK": [], "FAMC": [], "FAMO": [], "FOCD": [], "FERNAME": []},
                         "RESIDUES AND ORGANIC FERTILIZER": {"RDATE": [], "RCOD": [], "RAMT": [], "RESN": [], "RESP": [],
                                                             "RESK": [], "RINP": [], "RDEP": [], "RMET": [], "RENAME": []},
                         "CHEMICAL APPLICATIONS": {"CDATE": [], "CHCOD": [], "CHAMT": [], "CHME": [], "CHDEP": [], "CHT": [], "CHNAME": []},
                         "TILLAGE": {"TL": [], "TDATE": [], "TIMPL": [], "TDEP": [], "TNAME": []},
                         "ENVIRONMENT MODIFICATIONS": {"ODATE": [], "EDAY": [], "ERAD": [], "EMAX": [], "EMIN": [], "ERAIN": [],
                                                       "ECO2": [], "EDEW": [], "EWIND": [], "ENVNAME": []},
                         "HARVEST DETAILS": {"HDATE": [], "HSTG": [], "HCOM": [], "HSIZE": [], "HPC": [],
                                             "HBPC": [], "HNAME": []},
                         "SIMULATION CONTROLS": {"GENERAL": [], "NYERS": [], "NREPS": [], "START": [], "SDATE": [], "RSEED": [], "SNAME": [], "SMODEL": [],
                                                 "OPTIONS": [], "WATER": [], "NITRO": [], "SYMBI": [], "PHOSP": [], "POTAS": [], "DISES": [], "CHEM": [], "TILL": [], "CO2": [],
                                                 "METHODS": [], "WTHER": [], "INCON": [], "LIGHT": [], "EVAPO": [], "INFIL": [], "PHOTO": [], "HYDRO": [], "NSWIT": [], "MESOM": [], "MESEV": [], "MESOL": [],
                                                 "MANAGEMENT": [], "PLANT": [], "IRRIG": [], "FERTI": [], "RESID": [], "HARVS": [],
                                                 "OUTPUTS": [], "FNAME": [], "OVVEW": [], "SUMRY": [], "FROPT": [], "GROUT": [], "CAOUT": [], "WAOUT": [], "NIOUT": [], "MIOUT": [], "DIOUT": [], "VBOSE": [], "CHOUT": [], "OPOUT": [],
                                                 "PLANTING": [], "PFRST": [], "PLAST": [], "PH2OL": [], "PH2OU": [], "PH2OD": [], "PSTMX": [], "PSTMN": [],
                                                 "IRRIGATION": [], "IMDEP": [], "ITHRL": [], "ITHRU": [], "IROFF": [], "IMETH": [], "IRAMT": [], "IREFF": [],
                                                 "NITROGEN": [], "NMDEP": [], "NMTHR": [], "NAMNT": [], "NCODE": [], "NAOFF": [],
                                                 "RESIDUES": [], "RIPCN": [], "RTIME": [], "RIDEP": [],
                                                 "HARVEST": [], "HFRST": [], "HLAST": [], "HPCNP": [], "HPCNR": []}
                         }
            simismo.dic = dic_filex

        # Las secciones posibles en un documento FILEX
        simismo.secciones = {}
        for i in simismo.dic:
            simismo.secciones[i] = {"Prin":(), "Fin":()}

    # Lee un archivo FILEX para uso en Python. "Documento" es la ubicación del archivo FILEX en la computadora.
    def leer(simismo, documento):
        # Borar datos, si existen
        for i in simismo.dic:
            for j in simismo.dic[i]:
                simismo.dic[i][j] = []

        with open(documento, "r") as d:
            doc=[]
            for línea in d:
                doc.append(línea)

        ### Leer todas las secciones

        # Sección "GENERAL"
        simismo.dic["PEOPLE"]=doc[doc.index('@PEOPLE\n')+1].replace('\n', '')
        simismo.dic["ADDRESS"]=doc[doc.index('@ADDRESS\n')+1].replace('\n', '')
        simismo.dic["SITE(S)"]=doc[doc.index('@SITE\n')+1].replace('\n', '')

        for línea in doc:
            # Sección "GENERAL" (cont.)
            vars_parcela = "PAREA  PRNO  PLEN  PLDR  PLSP  PLAY HAREA  HRNO  HLEN  HARM".split()
            if "@ PAREA" in línea:
                valores_parcela = doc[
                    doc.index("@ PAREA  PRNO  PLEN  PLDR  PLSP  PLAY HAREA  HRNO  HLEN  HARM.........\n")+1
                ].split()
                for a in simismo.dic['GENERAL']:
                    simismo.dic['GENERAL'][a] = valores_parcela[vars_parcela.index(a)]
            simismo.dic["NOTES"]=doc[doc.index('@NOTES\n')+1]

            # Sección "EXP.DETAILS"
            if "*EXP.DETAILS" in línea:
                simismo.dic["EXP.DETAILS"]=línea.replace("*EXP.DETAILS: ", "").replace('\n', '')

            # Leer las secciones aparte la "GENERAL" y la "EXP.DETAILS"
            for otra in simismo.secciones:
                if otra != "EXP.DETAILS" and otra != "":
                    simismo.decodar(doc,otra)

    def escribir(simismo, documento):      # Escribe un documento FILEX para uso en DSSAT
        for i in simismo.dic:    # Llenar variables vacíos con -99 (el código de DSSAT para datos que faltan)
            if type(prueba.dic[i]) is dict:
                for j in simismo.dic[i]:
                    if not len(simismo.dic[i][j]): simismo.dic[i][j] = [["-99"]]
            else:
                if simismo.dic[i]=='': simismo.dic[i]= [["-99"]]
        with open("FILEX.txt", "r") as d:    # Abrir el patrón general para archivos FILEX
            doc=[]
            for línea in d:
                doc.append(línea)
            doc.append("\n")  # Terminar con una línea vacía para marcar el fin del documento


        for otra in simismo.secciones:
            if otra!="EXP.DETAILS":
                simismo.encodar(doc,otra)

        with open(documento, "w") as d:   # Salvar la carpeta FILEX en la ubicación contenida en "documento"
            texto = ''
            d.write(texto.join(doc))
            # for x in range(1, 11):
            # print('{0:25d} {1:3d} {2:4d}'.format(x, x*x, x*x*x))

        def decodar(self, doc, sección):  # Esta funcción convierte una sección de FILEX en un diccionario Python.
        # Encuentra la ubicación del principio y del fin de cada sección
        prin = fin = None
        for línea in doc:
            if "*" in línea and sección in línea:
                prin = doc.index(línea)
                fin = doc.index("\n",prin)
                break

        if prin:  # Si existe la sección
            for línea,texto in enumerate(doc[prin:fin-1],start=prin):
                if "@" in texto:
                    variables = texto.split()[1:]
                    if sección == "GENERAL": variables = texto.replace("@",'').split()
                    for a,var in enumerate(variables):
                        if '.' in var:      # Para el caso donde variables en FILEX están separados por '.' y no por ' '
                            variable = variables[a].split('.')
                            variable.reverse()
                            for b in variable:
                                if len(b): variables.insert(a,b)
                            variables.remove(var)
                    i=línea+1
                    while "@" not in doc[i] and len(doc[i].replace('\n',''))>0:
                        if isinstance(simismo,Filex):
                            valores = doc[i].replace('\n','')[2:]
                            nivel = doc[i].split()[0]
                            if not nivel.isdigit():
                                nivel = 1
                            else: nivel = int(nivel)
                        else:
                            valores = doc[i].replace('\n','')[2:]

                        for j,var in enumerate(variables):
                            if var in simismo.dic[sección]:  # Si la variable existe en la base de datos de DSSAT
                                if isinstance(simismo,Filex):
                                    if len(simismo.dic[sección][var]) < nivel: simismo.dic[sección][var].append([])
                                    simismo.dic[sección][var][nivel-1].append(valores[:prop_vars[var]+1].strip())
                                else:
                                    simismo.dic[sección][var].append(valores[:prop_vars[var]+1].strip())
                                valores = valores[prop_vars[var]+1:]
                        i += 1

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
    files = Files()
    for var in suelo.dic:
        if var in conv_var_suelos.keys():
            files.dic[conv_var_suelos[var]["DSSAT"]] = suelo.dic[var]
    files.escribir(cod_suelo=nombre)

    # Crear un objeto de carpeta de variedades DSSAT para manejar los datos
    filec = Filec(nombre=nombre, cultivo=cultivo, modelo=modelo)
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
# # Pruebas:
# prueba = Files()
# prueba.leer('IB00000002')
# prueba.escribir('IB00000002')
# # prueba = filex()
# # prueba.leer('C:\DSSAT45\Maize\BRPI0202.MZX')
# # prueba.escribir('C:\DSSAT45\Maize\BRPI0202_PRUEBA.MZX')

def decodar(self, doc, sección):  # Esta funcción convierte una sección de FILEX en un diccionario Python.
        # Encuentra la ubicación del principio y del fin de cada sección
        for línea in doc:
            if "*" in línea and sección in línea:
                prin = doc.index(línea)
                fin = doc.index("\n",prin)
                break
            else:
                prin = fin = None
        if prin:  # Si existe la sección
            for línea,texto in enumerate(doc[prin:fin-1],start=prin):
                if "@" in texto:
                    variables = texto.split()[1:]
                    if sección == "GENERAL": variables = texto.replace("@",'').split()
                    for a,var in enumerate(variables):
                        if '.' in var:      # Para el caso donde variables en FILEX están separados por '.' y no por ' '
                            variable = variables[a].split('.')
                            variable.reverse()
                            for b in variable:
                                if len(b): variables.insert(a,b)
                            variables.remove(var)
                    i=línea+1
                    while "@" not in doc[i] and len(doc[i].replace('\n',''))>0:
                        if isinstance(self,Filex):
                            valores = doc[i].replace('\n','')[2:]
                            nivel = doc[i].split()[0]
                            if not nivel.isdigit():
                                nivel = 1
                            else: nivel = int(nivel)
                        else:
                            valores = doc[i].replace('\n','')[2:]

                        for j,var in enumerate(variables):
                            if var in self.dic[sección]:  # Si la variable existe en la base de datos de DSSAT
                                if isinstance(self,Filex):
                                    if len(self.dic[sección][var]) < nivel: self.dic[sección][var].append([])
                                    self.dic[sección][var][nivel-1].append(valores[:prop_vars[var]+1].strip())
                                else:
                                    self.dic[sección][var].append(valores[:prop_vars[var]+1].strip())
                                valores = valores[prop_vars[var]+1:]
                        i += 1

    def encodar(self, doc, sección):
        prin = 0
        while sección not in doc[prin]:    # Encontrar el principio de la sección
            prin += 1
        línea = prin
        while línea != doc.index("\n",prin):  # Mientras no llegamos al fin de la sección
            print("línea", línea)
            línea += 1
            texto = doc[línea]
            print("texto", texto)
            if '{' in texto:   # Si la línea tiene variables a llenar
                var = texto[texto.index("{")+2:texto.index("]")]  # Leer el primer variable de la línea (para calcular el número de niveles y repeticiones más adelante)
                copia = texto   # Copiar la línea vacía (en caso que hayan otras líneas que agregar)
                for i, a in enumerate(self.dic[sección][var]):    # Para cada nivel de tratamiento
                    for j,b in enumerate(a):     # Para cada repetición del nivel (por ej., varias aplicaciones de riego al mismo tratamiento)
                        if isinstance(self, Filex):
                            if sección != "GENERAL" and sección != "EXP. DETAILS": texto = " " + str(i + 1) + copia # Escribir el nivel del tratamiento
                        texto = texto.replace("]", "][" + str(i) + "][" + str(j) + "]").replace("{[", "{" + sección + "[")
                        print("texto",texto)
                        texto = texto.format(**self.dic)
                        doc.insert(línea, texto)
                        línea += 1
                doc.remove(copia)