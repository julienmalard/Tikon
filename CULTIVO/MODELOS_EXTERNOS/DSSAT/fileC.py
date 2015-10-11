import os
from CULTIVO.MODELOS_EXTERNOS.DSSAT.DSSAT import DocDssat


# Objeto para representar documentos de typo FILEC de DSSAT (información de variedades de cultivos)
class FileC(DocDssat):
    def __init__(simismo, nombre, cultivo, modelo, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Esta variable se initializa como DocDssat

        simismo.nombre = nombre
        simismo.cultivo = cultivo
        simismo.modelo = modelo
        simismo.dic = {"VAR#": "TIK" + simismo.nombre[0:3], "VRNAME": simismo.nombre[0:14], "ECO#": "", "CSDL": [],
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

        # La lista de los documentos de genética de cultivos disponibles para DSSAT
        simismo.doc_cult_disp = {"MZCER046": {"Maíz": "MZCER046"},
                                 "MZIXM046": {"Maíz": "MZIXM046"},
                                 "CRGRO046": {"Repollo": "CBGRO046", "Frijol": "BNGRO046", "Maní": "PNGRO046",
                                              "Tomate": "TMGRO046", "Pimiento": "PRGRO046"},
                                 "PTSUB046": {"Papa": "PTSUB046"}}

    def leer(simismo):
        # Los datos de suelos están combinados, con muchos en la misma carpeta.
        # Este programa primero verifica si se ubica el suelo en la carpeta "Python.sol".
        # Si el suelo no se ubica allá, buscará en los otros documentos de la carpeta "DSSAT45/soil/"

        documento = simismo.doc_cult_disp[simismo.modelo][simismo.cultivo]

        encontrado = False
        for tipo_doc in [".cul", ".eco"]:
            with open(os.path.join(simismo.dir_DSSAT, "Genotype", documento, tipo_doc), "r") as d:
                for línea in d:
                    if "!" in línea:
                        pass  # Saltar los comentarios
                    elif "@" in línea:
                        variables = línea.replace('.', ' ').replace('@', ' ').split()
                    elif simismo.nombre[0:14] in línea:
                        datos = línea.split()
                        for númdato, dato in enumerate(datos):
                            if variables[númdato] in simismo.dic.keys():
                                simismo.dic[variables[númdato]] = dato
                        encontrado = True
                        break
        if not encontrado:
            return "No se encontró la variedad " + simismo.nombre + " para el cultivo " + simismo.cultivo + "."

    def escribir(simismo):
        documento = simismo.doc_cult_disp[simismo.modelo][simismo.cultivo]
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

            with open(os.path.join(simismo.dir_DSSAT, "Genotype", documento, tipo_doc), "r+") as d:
                doc = d.readlines()
                for i, línea in enumerate(doc):
                    if simismo.nombre[0:14] in línea:
                        del doc[i]
                        break
                    else:
                        continue
                doc.append(nuevo_cultivo)
                d.seek(0)
                d.truncate()  # Borrar el documento
                d.write(''.join(doc))
