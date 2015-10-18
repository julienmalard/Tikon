import os
import datetime as ft

from CULTIVO.MODELOS_EXTERNOS.DSSAT.fileX import FileX
from CULTIVO.MODELOS_EXTERNOS.DSSAT.fileS import FileS
from CULTIVO.MODELOS_EXTERNOS.DSSAT.fileW import FileW
from CULTIVO.MODELOS_EXTERNOS.DSSAT.fileC import FileC


class Experimento(object):
    def __init__(simismo, carpeta, suelo, variedad, meteo, cultivo, parcela):
        simismo.directorio = carpeta  # Donde vamos a guardar las carpetas de ingreso y egreso de DSSAT
        simismo.variedad = variedad
        simismo.suelo = suelo
        simismo.meteo = meteo
        simismo.cultivo = cultivo
        simismo.parcela = parcela

    def gen_ingresos(simismo):

        # Una función para convertir objetos TIKON de suelos, clima y variedades a objetos de documentos DSSAT
        def convertir(obj, documento_conv):
            conversiones = {}
            with open(os.path.join(os.getcwd(), "CULTIVO", 'MODELOS_EXTERNOS', documento_conv)) as d:
                    col = ()
                    for núm_línea, línea in enumerate(d):
                        if núm_línea == 0:
                            # La columna con los variables del modelo
                            col = línea.replace("\n", "").split(';').index('DSSAT')
                        else:
                            # Para cada línea que sigue, leer el variable DSSAT que corresponde con el variable TIKON
                            datos = línea.replace("\n", "").split(';')
                            var_tikon = datos[0]
                            var_dssat = datos[col]
                            conversiones[var_tikon] = var_dssat
            # Crear el objeto de documento DSSAT apropiado
            if type(obj) is FileS:
                documento = FileS()
            elif type(obj) is FileW:
                documento = FileW()
            elif type(obj) is FileC:
                documento = FileC()
            elif type(obj) is dict:  # Así que le podamos pasar una parte del diccionario de un FILEX también
                return conversiones
            else:
                return False

            # Llenar el diccionario del documento basado en el diccionario del documento
            for var_tikon in obj.dic:
                documento.dic[conversiones[var_tikon]] = obj.dic[var_tikon]
                if var_tikon == "Fecha":  # Convertir fechas al formato AADDD de DSSAT
                    fecha = obj.dic[var_tikon]
                    if type(fecha) is str:
                        f = ft.datetime(1, 1, 1)
                        fecha = f.strptime(fecha, '%Y-%m-%d')
                    documento.dic[conversiones[var_tikon]] = str(fecha.date().year)[-2:] + fecha.date().strftime('%j')
            return documento

        # Crear objectos de documento DSSAT para la variedad, el suelo y el clima
        filec = convertir(simismo.variedad, 'Variables_variedades.csv')
        files = convertir(simismo.suelo, 'Variables_suelo.csv')
        filew = convertir(simismo.meteo, 'Variables_meteo.csv')

        # Escribir los documentos de ingresos DSSAT
        filec.escribir()
        files.escribir()
        filew.escribir()

        # Generar la carpeta FILEX
        filex = FileX()
        filex.dic["EXP.DETAILS"] = "Autogenerado por Tikon el %d" % ft.datetime.now().strftime("%d-%m-%Y %H:%M")

        filex.dic["GENERAL"]["People"] = "Tikon fue desarrollado por Julien Malard y Marcela Rojas Díaz."
        filex.dic["GENERAL"]["Address"] = "Universidad McGill, Dept de Biorecursos, Saint-Anne-de-Bellevue, Canadá"
        filex.dic["GENERAL"]["NOTES"] = "Contacto: julien.malard@mail.mcgill.ca"
        filex.dic["GENERAL"]["PAREA"] = simismo.parcela["Área"]
        filex.dic["GENERAL"]["PRNO"] = simismo.parcela["Surcos"]
        filex.dic["GENERAL"]["PLDR"] = simismo.parcela["Long_surcos"]

        filex.dic["TREATMENTS"]["R"] = 1
        filex.dic["TREATMENTS"]["O"] = 0
        filex.dic["TREATMENTS"]['O'] = 0
        for i in ['CU', 'FL', 'SA', 'IC', 'MP', 'MI', 'MF', 'MR', 'MC', 'MT', 'ME', 'MH', 'SM']:
            filex.dic["TREATMENTS"][i] = 1

        filex.dic["CULTIVARS"]['CR'] = simismo.cultivo.cód_cultivo
        filex.dic["CULTIVARS"]['INGEN'] = filec.dic['VAR#']
        filex.dic["CULTIVARS"]['CNAME'] = filec.dic['VRNAME']

        filex.dic["FIELDS"]["ID_FIELD"] = simismo.parcela.nombre[:4] + '0001'
        filex.dic["FIELDS"]["WSTA"] = filew.dic["INSI"] + 'TKON'
        filex.dic["FIELDS"]['PLOB'] = simismo.parcela["Pendiente_orientación"]
        filex.dic["FIELDS"]['FLST'] = simismo.parcela["Piedras"]
        filex.dic["FIELDS"]['SLTX'] = files.dic["SLTX"]
        filex.dic["FIELDS"]['SLDP'] = files.dic["SLDP"]
        filex.dic["FIELDS"]['ID_SOIL'] = files.dic['ID_SOIL']

        # Poner los parámetros de manejo del objeto "PARCELA" en la sección apropiada del diccionario de fileX
        manejo = simismo.parcela['Manejo']

        for sección in ["PLANTING DETAILS", "FERTILIZERS (INORGANIC)", "RESIDUES AND ORGANIC FERTILIZER",
                        "IRRIGATION AND WATER MANAGEMENT", "TILLAGE", "HARVEST DETAILS"]:
            conv_dssat = convertir(filex.dic[sección], 'Variables_manejo.csv')
            for var in conv_dssat:
                if var in manejo and conv_dssat[var] in filex.dic[sección]:
                    filex.dic[sección][conv_dssat[var]] = manejo[var]

        # Areglar las controles de simulación
        filex.dic["SIMULATION CONTROLS"]['GENERAL'] = 'GE'
        filex.dic["SIMULATION CONTROLS"]['NYERS'] = 1
        filex.dic["SIMULATION CONTROLS"]['NREPS'] = 1
        filex.dic["SIMULATION CONTROLS"]['START'] = 'S'
        filex.dic["SIMULATION CONTROLS"]['SDATE'] = simismo.parcela['Fecha_init']
        filex.dic["SIMULATION CONTROLS"]['RSEED'] = 88
        filex.dic["SIMULATION CONTROLS"]['OPTIONS'] = 'OP'
        filex.dic["SIMULATION CONTROLS"]['WATER'] = 'Y'
        filex.dic["SIMULATION CONTROLS"]['NITRO'] = 'Y'
        filex.dic["SIMULATION CONTROLS"]['SYMBI'] = 'Y'
        filex.dic["SIMULATION CONTROLS"]['PHOSP'] = 'Y'
        filex.dic["SIMULATION CONTROLS"]['POTAS'] = 'Y'
        filex.dic["SIMULATION CONTROLS"]['DISES'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['CHEM'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['CO2'] = 'M'
        filex.dic["SIMULATION CONTROLS"]['METHODS'] = 'ME'
        filex.dic["SIMULATION CONTROLS"]['WTHER'] = 'M'
        filex.dic["SIMULATION CONTROLS"]['INCON'] = 'M'
        filex.dic["SIMULATION CONTROLS"]['LIGHT'] = 'E'
        filex.dic["SIMULATION CONTROLS"]['EVAPO'] = 'R'
        filex.dic["SIMULATION CONTROLS"]['INFIL'] = 'S'
        filex.dic["SIMULATION CONTROLS"]['PHOTO'] = 'L'
        filex.dic["SIMULATION CONTROLS"]['HYDRO'] = 'R'
        filex.dic["SIMULATION CONTROLS"]['NSWIT'] = 1
        filex.dic["SIMULATION CONTROLS"]['MESOM'] = 'G'
        filex.dic["SIMULATION CONTROLS"]['MESEV'] = 'S'
        filex.dic["SIMULATION CONTROLS"]['MESOL'] = 2
        filex.dic["SIMULATION CONTROLS"]['MANAGEMENT'] = 'MG'
        filex.dic["SIMULATION CONTROLS"]['PLANT'] = 'R'
        if manejo['Irrig']:
            if manejo['Irrig_auto']:
                filex.dic["SIMULATION CONTROLS"]['IRRIG'] = 'A'
            else:
                filex.dic["SIMULATION CONTROLS"]['IRRIG'] = 'R'
        else:
            filex.dic["SIMULATION CONTROLS"]['IRRIG'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['FERTI'] = 'R'
        filex.dic["SIMULATION CONTROLS"]['RESID'] = 'R'
        filex.dic["SIMULATION CONTROLS"]['HARVS'] = 'M'
        filex.dic["SIMULATION CONTROLS"]['OUTPUTS'] = 'OU'
        filex.dic["SIMULATION CONTROLS"]['FNAME'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['OVVEW'] = 'Y'
        filex.dic["SIMULATION CONTROLS"]['SUMRY'] = 'Y'
        filex.dic["SIMULATION CONTROLS"]['FROPT'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['GROUT'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['CAOUT'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['WAOUT'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['NIOUT'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['MIOUT'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['DIOUT'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['VBOSE'] = 0
        filex.dic["SIMULATION CONTROLS"]['CHOUT'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['OPOUT'] = 'N'
        filex.dic["SIMULATION CONTROLS"]['PLANTING'] = 'PL'
        filex.dic["SIMULATION CONTROLS"]['PFRST'] = -99
        filex.dic["SIMULATION CONTROLS"]['PLAST'] = -99
        filex.dic["SIMULATION CONTROLS"]['PH2OL'] = -99
        filex.dic["SIMULATION CONTROLS"]['PH2OU'] = -99
        filex.dic["SIMULATION CONTROLS"]['PH2OD'] = -99
        filex.dic["SIMULATION CONTROLS"]['PSTMX'] = -99
        filex.dic["SIMULATION CONTROLS"]['PSTMN'] = -99
        filex.dic["SIMULATION CONTROLS"]['IRRIGATION'] = 'IR'
        filex.dic["SIMULATION CONTROLS"]['IMDEP'] = '30'
        filex.dic["SIMULATION CONTROLS"]['ITHRL'] = '50'
        filex.dic["SIMULATION CONTROLS"]['ITHRU'] = '100'
        filex.dic["SIMULATION CONTROLS"]['IROFF'] = -99
        filex.dic["SIMULATION CONTROLS"]['IMETH'] = 'IR004'
        if manejo['Irrig_auto']:
            filex.dic["SIMULATION CONTROLS"]['IRAMT'] = -99
        else:
            filex.dic["SIMULATION CONTROLS"]['IRAMT'] = manejo['Cant_irrig_auto']
        filex.dic["SIMULATION CONTROLS"]['IREFF'] = 1
        filex.dic["SIMULATION CONTROLS"]['NITROGEN'] = 'NI'
        filex.dic["SIMULATION CONTROLS"]['NMDEP'] = -99
        filex.dic["SIMULATION CONTROLS"]['NMTHR'] = -99
        filex.dic["SIMULATION CONTROLS"]['NAMNT'] = -99
        filex.dic["SIMULATION CONTROLS"]['NCODE'] = -99
        filex.dic["SIMULATION CONTROLS"]['NAOFF'] = -99
        filex.dic["SIMULATION CONTROLS"]['RESIDUES'] = 'RE'
        filex.dic["SIMULATION CONTROLS"]['RIPCN'] = 100
        filex.dic["SIMULATION CONTROLS"]['RTIME'] = -99
        filex.dic["SIMULATION CONTROLS"]['RIDEP'] = 20
        filex.dic["SIMULATION CONTROLS"]['HARVEST'] = 'HA'
        filex.dic["SIMULATION CONTROLS"]['HFRST'] = 0
        filex.dic["SIMULATION CONTROLS"]['HLAST'] = -99
        filex.dic["SIMULATION CONTROLS"]['HPCNP'] = 100
        filex.dic["SIMULATION CONTROLS"]['HPCNR'] = 0

        # Escribir el documento FILEX en el directorio
        filex.escribir(os.path.join(simismo.directorio, 'TIKON.', simismo.cultivo.cód_cultivo, 'X'))

        # Generar la carpetar DSSBatch necesaria para controlar DSSAT desde el "símbolo del sistema"
        simismo.gen_dssbatch()

    def gen_dssbatch(simismo):
        with open("FILES.txt", "r") as d:    # Abrir el esquema general para archivos FILES
            esquema = []
            for línea in d:
                esquema.append(línea)
        esquema.append("\n")  # Terminar con una línea vacía para marcar el fin del documento

        dic = {"Cultivo": simismo.cultivo.cultivo,
               "FILEX": os.path.join(simismo.directorio, 'TIKON.', simismo.cultivo.cód_cultivo, 'X')
               }

        for núm_lín, línea in enumerate(esquema):
            if '{' in línea:
                esquema[núm_lín] = línea.format(**dic)
        esquema = ''.join(esquema)  # Lo que tenemos que escribir al documento DSSBatch

        # Guardar el documento DSSBatch
        with open(os.path.join(simismo.directorio, 'TIKON.', simismo.cultivo.cód_cultivo, 'X'), "w") as d:
            d.write(''.join(esquema))
