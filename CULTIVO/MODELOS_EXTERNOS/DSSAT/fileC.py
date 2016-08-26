import os

from CULTIVO.Controles import dir_DSSAT
from CULTIVO.Controles import sacar_modelos_disp


# Objeto para representar documentos de typo FILEC de DSSAT (información de variedades de cultivos)
class FileC(object):
    def __init__(símismo):

        símismo.dic = {'Cultivo': '', 'Modelo': '', 'VRNAME': '', 'VAR#': '', 'ECO#': '', 'ECONAME': '', 'CSDL': [],
                       'PPSEN': [], 'EM-FL': [], 'FL-SH': [], 'FL-SD': [], 'SD-PM': [], 'FL-LF': [], 'LFMAX': [],
                       'SLAVR': [], 'SIZLF': [], 'XFRT': [], 'WTPSD': [], 'SFDUR': [], 'SDPDV': [], 'PODUR': [],
                       'THRSH': [], 'SDPRO': [], 'SDLIP': [], 'MG': [], 'TM': [], 'THVAR': [], 'PL-EM': [],
                       'EM-V1': [], 'V1-JU': [], 'JU-R0': [], 'PM06': [], 'PM09': [], 'LNGSH': [], 'R7-R8': [],
                       'FL-VS': [], 'TRIFL': [], 'RWDTH': [], 'RHGHT': [], 'R1PPO': [], 'OPTBI': [], 'SLOBI': [],
                       'P1': [], 'P2': [], 'P5': [], 'G2': [], 'G3': [], 'PHINT': [], 'TBASE': [], 'TOPT': [],
                       'ROPT': [], 'P2O': [], 'DJTI': [], 'GDDE': [], 'DSGFT': [], 'RUE': [], 'KCAN': [], 'AX': [],
                       'ALL': [], 'PEAR': [], 'PSTM': [], 'G2_papa': [], 'G3_papa': [], 'PD': [], 'P2_papa': [],
                       'TC': [], 'RUE1': [], 'RUE2': [], 'P2_piña': [], 'P3_piña': [], 'G2_piña': [], 'G3_piña': []
                       }

        # El código para este cultivar
        símismo.dic["VAR#"] = "TIK" + símismo.dic["Nombre"][0:3]
        símismo.dic["ECO#"] = "TIK" + símismo.dic["Nombre"][0:3]

    def leer(símismo):

        # La lista de los documentos de genética de cultivos disponibles para DSSAT
        cult_disp = sacar_modelos_disp(símismo.dic['Cultivo'])
        documento = cult_disp[símismo.dic["Modelo"]]['Cód_modelo']

        encontrado = False
        for tipo_doc in [".cul", ".eco"]:
            with open(os.path.join(dir_DSSAT, "Genotype", documento, tipo_doc), "r") as d:
                for línea in d:
                    if "!" in línea:
                        pass  # Saltar los comentarios
                    elif "@" in línea:
                        variables = línea.replace('.', ' ').replace('@', ' ').split()
                    elif símismo.dic["Nombre"][0:14] in línea:
                        datos = línea.split()
                        for númdato, dato in enumerate(datos):
                            if variables[númdato] in símismo.dic.keys():
                                símismo.dic[variables[númdato]] = dato
                        encontrado = True
                        break
        if not encontrado:
            return "No se encontró la variedad %s para el cultivo %s." % (símismo.dic["Nombre"], símismo.dic["Cultivo"])

    def escribir(símismo):

        for i in símismo.dic:  # Llenar variables vacíos con -99 (el código de DSSAT para datos que faltan)
            for j in símismo.dic[i]:
                if not len(símismo.dic[i][j]):
                    símismo.dic[i][j] = ["-99"]

        cult_disp = sacar_modelos_disp(símismo.dic['Cultivo'])
        esquema = cult_disp[símismo.dic["Modelo"]]['Modelo']
        documento = cult_disp[símismo.dic["Modelo"]]['Cód_modelo']

        for tipo_doc in [".cul", ".eco"]:
            with open('GENOTIPO.txt', 'r') as d:
                doc = d.readlines()
            if tipo_doc == ".cul":
                esquema += "_CUL.txt"
            if tipo_doc == ".eco":
                esquema += '_ECO.txt'
            for i in doc:
                if esquema in i:
                    nuevo_cultivo = i[len(esquema) + 1:]
                    nuevo_cultivo += "\n"  # Terminar con una línea vacía para marcar el fin del documento

            nuevo_cultivo.format(**símismo.dic)

            with open(os.path.join(dir_DSSAT, "Genotype", documento, tipo_doc), "r+") as d:
                doc = d.readlines()
                for i, línea in enumerate(doc):
                    if símismo.dic["Nombre"][0:14] in línea:
                        del doc[i]
                        break
                    else:
                        continue
                doc.append(nuevo_cultivo)
                d.seek(0)
                d.truncate()  # Borrar el documento
                d.write(''.join(doc))
