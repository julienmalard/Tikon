import os
from CULTIVO.Controles import dir_DSSAT


# Objeto para representar documentos de typo FILEC de DSSAT (información de variedades de cultivos)
class FileC(object):
    def __init__(simismo):

        simismo.dic = {"Cultivo": "", "Modelo": "", "VRNAME": "", "VAR#": "", "ECO#": "", "ECONAME": "", "CSDL": [],
                       "PPSEN": [], "EM-FL": [], "FL-SH": [], "FL-SD": [], "SD-PM": [], "FL-LF": [], "LFMAX": [],
                       "SLAVR": [], "SIZLF": [], "XFRT": [], "WTPSD": [], "SFDUR": [], "SDPDV": [], "PODUR": [],
                       "THRSH": [], "SDPRO": [], "SDLIP": [], "MG": [], "TM": [], "THVAR": [], "PL-EM": [],
                       "EM-V1": [], "V1-JU": [], "JU-R0": [], "PM06": [], "PM09": [], "LNGSH": [], "R7-R8": [],
                       "FL-VS": [], "TRIFL": [], "RWDTH": [], "RHGHT": [], "R1PPO": [], "OPTBI": [], "SLOBI": [],
                       "P1": [], "P2": [], "P5": [], "G2": [], "G3": [], "PHINT": [], "TBASE": [], "TOPT": [],
                       "ROPT": [], "P2O": [], "DJTI": [], "GDDE": [], "DSGFT": [], "RUE": [], "KCAN": [], "AX": [],
                       "ALL": [], "PEAR": [], "PSTM": [], "G2_papa": [], "G3_papa": [], "PD": [], "P2_papa": [],
                       "TC": []
                       }

        # El código para este cultivar
        simismo.dic["VAR#"] = "TIK" + simismo.dic["Nombre"][0:3]
        simismo.dic["ECO#"] = "TIK" + simismo.dic["Nombre"][0:3]

        # La lista de los documentos de genética de cultivos disponibles para DSSAT
        simismo.cult_disp = {"MZCER046": {"Maíz": "MZCER046"},
                             "MZIXM046": {"Maíz": "MZIXM046"},
                             "CRGRO046": {"Repollo": "CBGRO046", "Frijol": "BNGRO046", "Maní": "PNGRO046",
                                          "Tomate": "TMGRO046", "Pimiento": "PRGRO046"},
                             "PTSUB046": {"Papa": "PTSUB046"}}

    def leer(simismo):
        # Los datos de suelos están combinados, con muchos en la misma carpeta.
        # Este programa primero verifica si se ubica el suelo en la carpeta "Python.sol".
        # Si el suelo no se ubica allá, buscará en los otros documentos de la carpeta "DSSAT45/soil/"

        documento = simismo.cult_disp[simismo.dic["Modelo"]][simismo.dic["Cultivo"]]

        encontrado = False
        for tipo_doc in [".cul", ".eco"]:
            with open(os.path.join(dir_DSSAT, "Genotype", documento, tipo_doc), "r") as d:
                for línea in d:
                    if "!" in línea:
                        pass  # Saltar los comentarios
                    elif "@" in línea:
                        variables = línea.replace('.', ' ').replace('@', ' ').split()
                    elif simismo.dic["Nombre"][0:14] in línea:
                        datos = línea.split()
                        for númdato, dato in enumerate(datos):
                            if variables[númdato] in simismo.dic.keys():
                                simismo.dic[variables[númdato]] = dato
                        encontrado = True
                        break
        if not encontrado:
            return "No se encontró la variedad %s para el cultivo %s." % (simismo.dic["Nombre"], simismo.dic["Cultivo"])

    def escribir(simismo):
        documento = simismo.cult_disp[simismo.dic["Modelo"]][simismo.dic["Cultivo"]]
        for i in simismo.dic:  # Llenar variables vacíos con -99 (el código de DSSAT para datos que faltan)
            for j in simismo.dic[i]:
                if not len(simismo.dic[i][j]):
                    simismo.dic[i][j] = ["-99"]

        for tipo_doc in [".cul", ".eco"]:
            esquema = documento[-2]

            with open('GENOTIPO.txt', 'r') as d:
                if tipo_doc == ".cul":
                    esquema += "_CUL.txt"
                if tipo_doc == ".eco":
                    esquema += '_ECO.txt'
                doc = d.readlines()
                for i in doc:
                    if esquema in i:
                        nuevo_cultivo = i[len(esquema) + 1:]
                        nuevo_cultivo += "\n"  # Terminar con una línea vacía para marcar el fin del documento

            nuevo_cultivo.format(**simismo.dic)

            with open(os.path.join(dir_DSSAT, "Genotype", documento, tipo_doc), "r+") as d:
                doc = d.readlines()
                for i, línea in enumerate(doc):
                    if simismo.dic["Nombre"][0:14] in línea:
                        del doc[i]
                        break
                    else:
                        continue
                doc.append(nuevo_cultivo)
                d.seek(0)
                d.truncate()  # Borrar el documento
                d.write(''.join(doc))
