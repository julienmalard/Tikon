from COSO import Coso
import numpy as np
import scipy as sp


class Insecto(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada insecto
        simismo.dic_base = dict(ciclo_vida="", tipo_ecuaciones="")
        simismo.ext = "int"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        super().__init__(*args, **kwargs)  # Esta clase se initializa como describido en Coso
        # Crear instancias de etapas de desarrollo según el ciclo de vida del insecto
        simismo.fases = {}
        if simismo.dic["ciclo_vida"] == "simple":
            simismo.fases = dict(Adulto=Fase(simismo.nombre + "_adulto"))
            simismo.fases["Adulto"].dic["fuente"] = simismo.fases["Adulto"]
        elif simismo.dic["ciclo_vida"] == "dos_fases":
            simismo.fases = dict(Juvenil=Fase(simismo.nombre + "_juvenil"), Adulto=Fase(simismo.nombre + "_adulto"))
            simismo.fases["Juvenil"].dic["fuente"] = simismo.fases["Adulto"]
            simismo.fases["Adulto"].dic["fuente"] = simismo.fases["Juvenil"]
        elif simismo.dic["ciclo_vida"] == "cuatro_fases":
            simismo.fases = dict(Huevo=Fase(simismo.nombre + "_huevo"), Juvenil=Fase(simismo.nombre + "_juvenil"),
                                 Pupa=Fase(simismo.nombre + "_pupa"), Adulto=Fase(simismo.nombre + "_adulto"))
            simismo.fases["Huevo"].dic["fuente"] = simismo.fases["Adulto"]
            simismo.fases["Juvenil"].dic["fuente"] = simismo.fases["Huevo"]
            simismo.fases["Pupa"].dic["fuente"] = simismo.fases["Juvenil"]
            simismo.fases["Adulto"].dic["fuente"] = simismo.fases["Pupa"]
        elif "estadios" in simismo.dic["ciclo_vida"].lower():  # Permite incluir varios números de estadios de larvas
            núm_estadios = int(simismo.dic["ciclo_vida"].split('=')[1])
            simismo.fases = dict(Pupa=Fase(simismo.nombre + "_pupa"))
            for i in range(1, núm_estadios + 1):
                simismo.fases["Juvenil" + str(i)] = Fase(simismo.nombre + "_estadio_" + str(i))
                if i == 1:
                    simismo.fases["Juvenil" + str(i)].dic["fuente"] = simismo.fases["Pupa"]
                else:
                    simismo.fases["Juvenil" + str(i)].dic["fuente"] = simismo.fases["Juvenil" + str(i - 1)]
            simismo.fases["Pupa"].dic["fuente"] = simismo.fases["Juvenil" + str(núm_estadios)]
        else:
            print("Ciclo de vida no reconocido.")

        # Para guardar los datos de poblaciones
        simismo.pob = {}
        for fase in simismo.fases:
            simismo.pob[fase] = ()

    # Esta función inicializa el insecto basado en la red trófica utilizada
    def ejec(simismo, otros_insectos):
        for fase in simismo.fases:
            simismo.fases[fase].ejec(otros_insectos, simismo.dic["ciclo_vida"])

    # Esta función calcula los cambions de población de un insecto (para cada etapa de desarrollo del insecto)
    def incr(simismo, paso, tipo_ecuaciones, estado_cultivo):
        # El tipo de ecuación se puede especificar para cada tipo de insecto, en cual caso toma precedencia sobre
        # el tipo de ecuación especificado para la red
        if len(simismo.dic["tipo_ecuaciones"]):
            tipo_ecuaciones = simismo.dic["tipo_ecuaciones"]
        for fase in simismo.fases:
            simismo.fases[fase].incr(paso, tipo_ecuaciones, estado_cultivo)

    # Esta función implementa los cambions de población de un insecto (asegura que los cambios de población se
    # hacen independentamente del orden en cual se calculan los cambios)
    def actualizar(simismo):
        for fase in simismo.fases:
            simismo.fases[fase].actualizar()
            simismo.pob[fase] = simismo.fases[fase].pob


class Fase(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada insecto
        simismo.dic_base = dict(Depredadores=[], Presas=[], coefs={})
        simismo.ext = "fase"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        super().__init__(*args, **kwargs)  # Esta clase se initializa como describido en Coso

        simismo.ciclo_vida = ""
        # Para poner las presas y deprededores en la red actual
        simismo.depredadores_act = []
        simismo.presas_act = []
        # La población de la etapa del insecto
        simismo.pob = 0
        # Una lista para guardar una historia de transiciones entre fases
        simismo.hist_pob = []
        simismo.transición = 0  # La transición a otras etapas
        simismo.cambio_pob = 0  # El cambió de población en cada etapa de tiempo
        simismo.predación = {}  # Para guardar la cantidad de otros insectos consumidos

    # Esta función inicializa el insecto basado en la red trófica utilizada
    def ejec(simismo, otros_insectos, ciclo_vida):
        simismo.ciclo_vida = ciclo_vida

        # Utilizar sólamente los depredadoes y las presas en la red trófica utilizada
        for depredador in simismo.dic["Depredadores"]:
            if depredador.nombre.split('_')[0] in otros_insectos:
                simismo.depredadores_act.append(depredador)
        for presa in simismo.dic["Presas"]:
            # Si la presa es un otro insecto y existe en la red agroecológica especificada
            if type(presa) is Fase and presa.nombre.split('_')[0] in otros_insectos:
                if presa not in simismo.presas_act:
                    simismo.presas_act.append(presa)
            elif type(presa) is str:  # Si la "presa" es un cultivo
                if presa not in simismo.presas_act:
                    simismo.presas_act.append(presa)

    def incr(simismo, paso, tipo_ecuaciones, estado_cultivo):

        simismo.cambio_pob = 0  # El cambio de población esta etapa de tiempo

        # Ecuaciones de mortalidad por deprededor
        def depredación(tipo):
            pred = 0
            if tipo == "LV":
                for depred in simismo.depredadores_act:
                    pred += depred.pob * simismo.dic["coefs"][depred.nombre]
                return pred
            elif tipo == "competitivo":  # Presas "compiten" para el tiempo de los depredadores
                for depred in simismo.depredadores_act:
                    comida_depred = 0
                    comida_crít_depred = depred.dic["coefs"]["comida_crít"] * depred.pob
                    for presa in depred.presas_act:
                        if type(presa) is Fase:  # Si la presa es un insecto
                            comida_depred += presa.pob * depred.dic["coefs"][presa.nombre]  # Consumo de presas
                        else:  # Sino, si la "presa" es un cultivo
                            comida_depred += estado_cultivo[presa] * coefs[presa]
                    if comida_depred > comida_crít_depred:  # Si hay demasiada comida
                        pred = (simismo.pob * depred.dic["coefs"][simismo.nombre])/comida_depred * comida_crít_depred * depred.pob
                    else:  # Si no hay demasiada comida
                        pred = depred.dic["coefs"][simismo.nombre] * depred.pob

                return pred
            else:
                return "Error en la calculación de la depredación."

        # Ecuaciones de crecimiento
        # Para ecuaciones Lotka-Volterra
        if tipo_ecuaciones == "Lotka-Voltera":
            if simismo.ciclo_vida is not "simple":
                return "Error: Tipo de ecuación Lotka-Voltera para insecto " + simismo.nombre + \
                       " no está disponible para insectos con ciclos de vida complejos."
            else:
                r = 0
                if type(simismo.presas_act[0]) is Fase:  # si el insecto es un depredador
                    for presa in simismo.presas_act:
                        r += presa.pob * simismo.dic["coefs"][presa.nombre]  # Consumo de presas
                elif type(simismo.presas_act[0]) is str:  # Si el insecto es un herbívoro
                    r = simismo.dic["coefs"]["r"]
                simismo.cambio_pob = r * simismo.pob * paso

                simismo.cambio_pob -= depredación("LV") * paso

        # Un tipo de ecuación con transición entre etapas de crecimiento del insecto
        elif tipo_ecuaciones == "etapas":
            # Crecimiento poblacional (por ejemplo, larvas aumentan por la eclosión de huevos). Notar que, a parte
            # del caso de un ciclo de vida simple, la fuente del crecimiento está externa a la fase actual y
            # "taza_crec" se refiere a la taza de conversión de la fase presente a la próxima fase.

            coefs = simismo.dic["coefs"]
            mortalidad = 0  # La mortalidad
            simismo.transición = 0  # La transición a la próxima etapa
            if "r" in coefs.keys():
                r = coefs["r"]

            # Una distribución triangular para calcular las transiciones de fases y la mortalidad natural
            # La distribución de población se pone a fecha con la conversión de individuos de la última fase
            simismo.hist_pob.append(simismo.dic["fuente"].transición)

            simismo.hist_pob = np.trim_zeros(simismo.hist_pob, "f")  # Quitar los 0s iniciales
            if not len(simismo.hist_pob):  # Si no queda nada, dejar un "0"
                simismo.hist_pob = [0]

            # Calcular transiciones de insectos a la próxima fase
            if "días_trans" in coefs.keys():
                for día, pob in enumerate(reversed(simismo.hist_pob)):
                    pendiente = -4/(coefs["días_trans"]**2)
                    if coefs["días_trans_prom"] < día:
                        pendiente = -pendiente
                    trans_día = pob * max(0,
                                          ((coefs["días_trans_prom"] - día) *
                                           pendiente + 2/coefs["días_trans"] +
                                           (coefs["días_trans_prom"] - día - 1) *
                                           pendiente + 2/coefs["días_trans"]) / 2) * paso
                    # TODO: La línea siguiente no debería de ser necesaria
                    if día > coefs["días_trans_prom"] + coefs["días_trans"]/2:
                        trans_día = pob
                    simismo.hist_pob[len(simismo.hist_pob) - día - 1] -= trans_día
                    simismo.transición += trans_día
                simismo.transición *= paso

            # Mortalidad dependiente de la edad
            if "días_mort" in coefs.keys():
                for día, pob in enumerate(reversed(simismo.hist_pob)):
                    pendiente = -4/(coefs["días_mort"]**2)
                    if simismo.dic["coefs"]["días_mort_prom"] < día:
                        pendiente = -pendiente
                    mort_día = pob * max(0,
                                         ((coefs["días_mort_prom"] - día) *
                                          pendiente + 2/coefs["días_mort"] +
                                          (coefs["días_mort_prom"] - día - 1) *
                                          pendiente + 2/coefs["días_mort"]) / 2)
                    # TODO: La línea siguiente no debería de ser necesaria
                    if día > coefs["días_mort_prom"] + coefs["días_mort"]/2:
                        mort_día = pob
                    simismo.hist_pob[len(simismo.hist_pob) - día - 1] -= mort_día
                    mortalidad += mort_día

            # Alternativamente, un factor de mortalidad constante
            elif "mortalidad" in coefs.keys():
                simismo.hist_pob = [x*(1-coefs["mortalidad"]) for x in simismo.hist_pob]
                mortalidad = simismo.pob * coefs["mortalidad"]

            # Reproducción dependiente de la edad
            reproducción = 0
            if "días_repr_prom" in coefs.keys():
                for día, pob in enumerate(reversed(simismo.hist_pob)):
                    pendiente = -4/(coefs["días_repr"]**2)
                    if coefs["días_repr_prom"] < día:
                        pendiente = -pendiente
                    reproducción += pob * max(0,
                                              ((coefs["días_repr_prom"] - día) *
                                               pendiente + 2/coefs["días_repr"] +
                                               (coefs["días_repr_prom"] - día - 1) *
                                               pendiente + 2/coefs["días_repr"]) / 2
                                              ) * r
            elif "r" in coefs.keys():
                reproducción = r * (simismo.pob - mortalidad)

            # Mortalidad por falta de comida (unidades: fracción)
            mort_com = 0
            if len(simismo.presas_act):
                comida = 0
                comida_crít = coefs["comida_crít"] * (simismo.pob + simismo.dic["fuente"].transición)
                for presa in simismo.presas_act:
                    if type(presa) is Fase:  # Si la presa es un insecto
                        comida += presa.pob * coefs[presa.nombre]  # Consumo de presas
                    else:  # Sino, si la "presa" es un cultivo
                        comida += estado_cultivo[presa] * coefs[presa]
                if comida <= comida_crít:  # Si falta comida...
                    if comida_crít == 0:  # Para evitar división por 0 en lo que sigue
                        mort_com = 1
                    else:
                        mort_com = 1 - (comida/comida_crít)

            # Mortalidad por deprededores (unidades: fracción)
            mort_depred = depredación("competitivo")

            # Mortalidad total (unidades: insectos)
            mortalidad += (mort_depred + mort_com) * simismo.pob

            # Suponemos que la mortalidad no natural afecta todas las edades igualmente
            if sum(simismo.hist_pob):
                simismo.hist_pob = [x*(1-(mort_depred + mort_com)/sum(simismo.hist_pob)) for x in simismo.hist_pob]
                simismo.hist_pob = [x*(x >= 0) for x in simismo.hist_pob]  # Asegurar que no tenemos sub-poblaciones negativas
                simismo.hist_pob = [round(x, 1) for x in simismo.hist_pob]

            # El cambio de población es la transición de la última fase, menos mortalidad y transiciones a nuevas fases
            simismo.cambio_pob = (- mortalidad - simismo.transición + simismo.dic["fuente"].transición) * paso
            # Añademos la reproducción a la transición a la próxima fase después del cálculo del cambio
            # en la población actual, porque la reproducción no sustraye de la población de una fase.
            simismo.transición += reproducción

        elif tipo_ecuaciones == "capacidad_de_carga":
            if simismo.ciclo_vida is not "simple":
                print('Error: Tipo de ecuación "Capacidad de Carga" para insecto ' + simismo.nombre +
                      'no está disponible para insectos con ciclos de vida complejos.')
            else:
                coefs = simismo.dic["coefs"]
                r = coefs["r"]
                K = 0
                for presa in simismo.presas_act:
                    if type(simismo.presas_act[0]) is Fase:  # Si el insecto es un depredador,
                        K += presa.pob * coefs[presa.nombre]  # el consumo de presas aumenta K.
                    elif type(simismo.presas_act[0]) is str:  # Y si el insecto es un herbívoro,
                        K += coefs[presa] * estado_cultivo[presa]  # K se determina por el estado del cultivo.
                if K > 0:  # Evitar dividir por 0 en la ecuación dN/dt = rN(K-N)/K
                    simismo.cambio_pob = r * simismo.pob * (K - simismo.pob)/K * paso
                else:
                    simismo.cambio_pob = -simismo.pob

                # Muertes por depredación determinadas por el modelo competitivo
                if len(simismo.depredadores_act):
                    simismo.cambio_pob -= depredación("competitivo") * paso

        else:
            print("Tipo de ecuación no reconocido.")


    def actualizar(simismo):

        # Implementar los cambios de poblaciones
        simismo.pob += simismo.cambio_pob
        simismo.cambio_pob = 0

        # Añadir fluctuaciones naturales a la población. ToDO: poner SIGMA como coeficiente del insecto
        simismo.pob = np.random.normal(simismo.pob, 1)
        simismo.pob = round(simismo.pob, 0)  # No sirve para nada 1 * 10^-18 de una avispa

        # Asegurarnos que, después de todas estas acrobacias matemáticas, no terminamos con menos de 0 insectos.
        if simismo.pob < 0:
            simismo.pob = 0
