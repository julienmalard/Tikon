import os

from CULTIVO.MODELOS_EXTERNOS.DSSAT.fileX import FileX
from CULTIVO.MODELOS_EXTERNOS.DSSAT.fileS import FileS
from CULTIVO.MODELOS_EXTERNOS.DSSAT.fileW import FileW
from CULTIVO.MODELOS_EXTERNOS.DSSAT.fileC import FileC
import datetime

# Objeto general para representar documentos de DSSAT (suelos, variedades, experimentos, etc.)
class DocDssat(object):
    def __init__(simismo):
        simismo.dir_DSSAT = "C:\DSSAT46"


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
                            var_DSSAT = datos[col]
                            conversiones[var_tikon] = var_DSSAT
            # Crear el objeto de documento DSSAT apropiado
            if type(obj) is FileS:
                documento = FileS()
            elif type(obj) is FileW:
                documento = FileW()
            elif type(obj) is FileC:
                documento = FileC()
            else:
                return False

            # Llenar el diccionario del documento basado en el diccionario del documento
            for var_tikon in obj.dic:
                documento.dic[conversiones[var_tikon]] = obj.dic[var_tikon]
            return documento

        # Crear objectos de documento DSSAT para la variedad, el suelo y el clima
        filec = convertir(simismo.variedad, 'Variables_variedades.csv')
        files = convertir(simismo.suelo, 'Variables_suelo.csv')
        filew = convertir(simismo.meteo, 'Variables_clima.csv')

        # Escribir los documentos de ingresos DSSAT
        filec.escribir()
        files.escribir()
        filew.escribir()

        # Generar la carpeta FILEX
        filex = FileX()
        filex.dic["EXP.DETAILS"] = "Autogenerado por Tikon el %d" % datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

        filex.dic["GENERAL"]["People"] = "Tikon fue desarrollado por Julien Malard y Marcela Rojas Díaz."
        filex.dic["GENERAL"]["Address"] = "Universidad McGill, Dept de Biorecursos, Saint-Anne-de-Bellevue, Canadá"
        filex.dic["GENERAL"]["NOTES"] = "Contacto: julien.malard@mail.mcgill.ca"
        filex.dic["GENERAL"]["PAREA"] = simismo.parcela.dic["Área"]
        filex.dic["GENERAL"]["PRNO"] = simismo.parcela.dic["Surcos"]
        filex.dic["GENERAL"]["PLDR"] = simismo.parcela.dic["Long_surcos"]

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
        filex.dic["FIELDS"]['PLOB'] = simismo.parcela.dic["Pendiente_orientación"]
        filex.dic["FIELDS"]['FLST'] = simismo.parcela.dic["Piedras"]
        filex.dic["FIELDS"]['SLTX'] = files.dic["SLTX"]
        filex.dic["FIELDS"]['SLDP'] = files.dic["SLDP"]
        filex.dic["FIELDS"]['ID_SOIL'] = files.dic['ID_SOIL']

        manejo = simismo.parcela.dic['Manejo']

        if manejo['Fecha_siembra'] == "":
            filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        if manejo['Fecha_emergencia'] == "":
            filex.dic["PLANTING DETAILS"]['EDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']
        filex.dic["PLANTING DETAILS"]['PDATE'] = manejo['Fecha_siembra']

        filex.dic["IRRIGATION AND WATER MANAGEMENT"] =
        filex.dic["FERTILIZERS (INORGANIC)"] =
        filex.dic["RESIDUES AND ORGANIC FERTILIZER"] =
        filex.dic["TILLAGE"] =
        filex.dic["HARVEST DETAILS"] =
        filex.dic["SIMULATION CONTROLS"] =

        filex.escribir(os.path.join(simismo.directorio, 'TIKON.', simismo.cultivo.cód_cultivo, 'X'))

        simismo.gen_DSSBatch()

    def gen_DSSBatch(simismo):
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
