import os
import numpy as np
from scipy.stats import norm

from COSO import Coso


# Representa un insecto
class Insecto(Coso):
    def __init__(símismo, nombre, huevo=False, njuvenil=None, pupa=False, adulto=True,
                 tipo_ecuaciones='capacidad_de_carga'):
        # El diccionario de los datos para cada insecto
        símismo.dic = dict(tipo_ecuaciones=tipo_ecuaciones)

        # Esta clase se initializa como describido en Coso
        directorio = os.path.join('Personales', 'Redes')
        super().__init__(ext="ins", nombre=nombre, directorio=directorio)

        # Crear instancias de etapas de desarrollo según el ciclo de vida del insecto
        símismo.fases = {}
        if huevo:
            símismo.fases['Huevo'] = Fase("%s_huevo" % símismo.nombre, directorio=directorio)

        for i in range(1, njuvenil+1):
            símismo.fases['Juvenil_%s' % i] = Fase("%s_juvenil_%s" % (símismo.nombre, i), directorio=directorio)

        if pupa:
            símismo.fases['Pupa'] = Fase("%s_pupa" % símismo.nombre, directorio=directorio)

        if adulto:
            símismo.fases['Adulto'] = Fase("%s_adulto" % símismo.nombre, directorio=directorio)

        # Crear las dependencias entre distintas fases:
        if huevo:
            if adulto:
                símismo.fases["Huevo"].dic["fuente"] = símismo.fases["Adulto"]
            elif pupa:
                símismo.fases["Huevo"].dic["fuente"] = símismo.fases["Pupa"]
            elif njuvenil:
                símismo.fases["Huevo"].dic["fuente"] = símismo.fases["Juvenil_%s" % (njuvenil + 1)]
            else:
                print('Se requiere al menos una fase activa para crear un insecto.')

        for i in range(1, njuvenil+1):
            if i > 1:
                símismo.fases['Juvenil_%s' % i].dic['fuente'] = símismo.fases["Juvenil_%s" % (i-1)]
            else:
                if huevo:
                    símismo.fases['Juvenil_%s' % i].dic['fuente'] = símismo.fases['Huevo']
                elif adulto:
                    símismo.fases['Juvenil_%s' % i].dic['fuente'] = símismo.fases['Adulto']
                elif pupa:
                    símismo.fases['Juvenil_%s' % i].dic['fuente'] = símismo.fases['Pupa']
                else:
                    print('Se requiere al menos una fase adulta o pupa para crear un insecto.')

        if pupa:
            if njuvenil:
                símismo.fases["Pupa"].dic["fuente"] = símismo.fases["Juvenil_%s" % (njuvenil + 1)]
            elif huevo:
                símismo.fases["Pupa"].dic["fuente"] = símismo.fases["Huevo"]
            elif pupa:
                símismo.fases["Pupa"].dic["fuente"] = símismo.fases['Pupa']
            elif adulto:
                símismo.fases["Pupa"].dic["fuente"] = símismo.fases['Adulto']
            else:
                print('Se requiere al menos una fase activa para crear un insecto.')

        if adulto:
            if pupa:
                símismo.fases["Adulto"].dic["fuente"] = símismo.fases["Pupa"]
            elif njuvenil:
                símismo.fases["Adulto"].dic["fuente"] = símismo.fases["Juvenil_%s" % (njuvenil + 1)]
            elif huevo:
                símismo.fases["Adulto"].dic["fuente"] = símismo.fases["Huevo"]
            else:
                símismo.fases["Adulto"].dic["fuente"] = símismo.fases["Adulto"]

        # Para guardar los datos de poblaciones
        símismo.pob = {}
        for fase in símismo.fases:
            símismo.pob[fase] = ()

    def secome(símismo, otro_insecto, fases_depred=None, fases_presa=None):
        # fases_depred y fases_presa tienen que ser listas de las fases del depredador y de la presa
        # Si no se especifiquen, se tomen todas las fases actias como depredadores y todas las fases como presas
        if not fases_depred:
            fases_depred = list(símismo.fases)
            # Quitar las fases inactivas (que no pueden comer a nada)
            if 'Pupa' in fases_depred:
                fases_depred.remove('Pupa')
            if 'Huevo' in fases_depred:
                fases_depred.remove('Huevo')
        # otros_insecto en forma de cadena de bits indica un cultivo (herbívoro) como 'presa'
        if type(otro_insecto) is str:
            for i in fases_depred:
                símismo.fases[i].dic['Presas'][otro_insecto] = otro_insecto
                return

        if not fases_presa:
            fases_presa = list(otro_insecto.fases)

        for i in fases_depred:
            for j in fases_presa:
                símismo.fases[i].dic['Presas'][otro_insecto.nombre + '_%s' % j] = otro_insecto.fases[j]
                otro_insecto.fases[j].dic['Depredadores'][símismo.nombre + '_%s' % i] = símismo.fases[i]

    # Esta función inicializa el insecto basado en la red trófica utilizada
    def ejec(símismo, otros_insectos):
        for fase in símismo.fases:
            símismo.fases[fase].ejec(tipo_ecuaciones=símismo.dic['tipo_ecuaciones'], otros_insectos=otros_insectos)

    # Esta función calcula los cambios de población de un insecto (para cada etapa de desarrollo del insecto)...
    # ... pero NO implementa los cambios calculados
    def incr(símismo, paso, estado_cultivo):
        tipo_ecuaciones = símismo.dic["tipo_ecuaciones"]
        for fase in símismo.fases:
            símismo.fases[fase].incr(paso, tipo_ecuaciones, estado_cultivo)

    # Esta función implementa los cambions de población de un insecto (asegura que los cambios de población se
    # hacen independentamente del orden en cual se calculan los cambios)
    def actualizar(símismo):
        for fase in símismo.fases:
            símismo.fases[fase].actualizar()
            símismo.pob[fase] = símismo.fases[fase].pob


# Unas clases prehechas para simplificar la creación de insectos
class Simple(Insecto):
    def __init__(self, nombre, huevo=False, tipo_ecuaciones='Lotka-Voltera'):
        super().__init__(nombre=nombre, huevo=huevo, njuvenil=0, adulto=True, tipo_ecuaciones=tipo_ecuaciones)


class MetamCompleta(Insecto):
    def __init__(self, nombre, huevo=True, njuvenil=1, adulto=True):
        super().__init__(nombre=nombre, huevo=huevo, njuvenil=njuvenil, pupa=True, adulto=adulto,
                         tipo_ecuaciones='etapas')


class MetamIncompleta(Insecto):
    def __init__(self, nombre, huevo=True, njuvenil=1, adulto=True):
        super().__init__(nombre=nombre,  huevo=huevo, njuvenil=njuvenil, pupa=False, adulto=adulto,
                         tipo_ecuaciones='etapas')


class Fase(Coso):
    def __init__(símismo, nombre, directorio):
        # El diccionario de los datos para cada insecto
        símismo.dic = dict(Depredadores={}, Presas={}, coefs={})
        # Esta clase se initializa como describido en Coso
        super().__init__(nombre=nombre, ext='fase', directorio=directorio)

        símismo.leer()

        # Listas para guardar poner las presas y deprededores en la red actual
        símismo.depredadores_act = []
        símismo.presas_act = []
        # La población de la etapa del insecto
        símismo.pob = 0
        # Una lista para guardar una historia de transiciones entre fases
        símismo.hist_pob = []
        símismo.transición = 0  # La transición a la próxima etapa, si aplica
        símismo.cambio_pob = 0  # El cambio de población a aplicar
        símismo.predación = {}  # Para guardar la cantidad de otros insectos consumidos

    # Esta función inicializa el insecto basado en la red trófica utilizada
    def ejec(símismo, tipo_ecuaciones, otros_insectos):

        # Utilizar sólamente los depredadoes y las presas en la red trófica utilizada
        for depredador in símismo.dic["Depredadores"]:
            if depredador.split('_')[0] in otros_insectos:
                símismo.depredadores_act.append(símismo.dic["Depredadores"][depredador])
        for presa in símismo.dic["Presas"]:
            # Si la presa es un otro insecto y existe en la red agroecológica especificada
            if type(símismo.dic["Presas"][presa]) is Fase and símismo.dic["Presas"][presa].nombre.split('_')[0] in\
                    otros_insectos.keys():
                if presa not in símismo.presas_act:
                    símismo.presas_act.append(símismo.dic["Presas"][presa])
            elif type(símismo.dic["Presas"][presa]) is str:  # Si la "presa" es un cultivo
                if presa not in símismo.presas_act:
                    símismo.presas_act.append(presa)

        # Asegurarse que tenemos todos los coeficientes necesarios:
        coefs = {'Lotka-Voltera': {'r': 'Tasa de crecimiento de base',
                                   'd': 'Tasa de muerte de base (para depredadores)',
                                   'Presas': {'a': 'Aumento a la tasa de crec por presa %s.'},
                                   'Depredadores': {'a': 'Disminución a la tasa de crecimiento por depredador %s.'}
                                   },
                 'capacidad_de-carga': {'r': 'Tasa de crecimiento de base',
                                        'Presas': {'a': 'Aumento a la capacidad de carga por presa %s.'},
                                        'comida_crít': 'La comida diaria necesaria por depredador/herbívoro',
                                        'Depredadores': {'a': 'La cantidad de presa %s que se puede comer por día.'}
                                        },
                 'etapas': {'trans_sigma': 'Rango de tiempo necesario para pasar a la próxima fase.',
                            'trans_mu': 'Número de días (en promedio) para pasar a la próxima fase.',
                            'mort_sigma': 'Rango de esperanza de vida. (opcional)',
                            'mort_mu': 'Esperanza de vida (promedio). (opcional)',
                            'mortalidad': 'Tasa de mortalidad constante (no opcional si no se especificó días_mort).',
                            'días_repr': 'Rango de vida reproductiva (opcional).',
                            'días_repr_prom': 'Mitad de la vida reproductiva (opcional).',
                            'r': 'Tasa de reproducción.'}
                 }
        valor = None

        for coef in coefs[tipo_ecuaciones]:
            if type(coefs[tipo_ecuaciones][coef]) is str:
                if coef not in símismo.dic['coefs'] or type(símismo.dic['coefs'][coef]) is str:
                    valor = input('%s: Ingresar valor para %s (%s): ' %
                                  (símismo.nombre, coef, coefs[tipo_ecuaciones][coef]))
                    if len(valor):
                        símismo.dic['coefs'][coef] = float(valor)
            elif type(coefs[tipo_ecuaciones][coef]) is dict:
                if coef == 'Presas':
                    for p in símismo.presas_act:
                        if type(p) is Fase and \
                                (p.nombre not in símismo.dic['coefs'] or type(símismo.dic['coefs'][p.nombre]) is str):
                            valor = input('%s: Ingresar valor para presa %s (%s): ' %
                                          (símismo.nombre, p.nombre, coefs[tipo_ecuaciones]['Presas']['a'] % p.nombre))
                            if len(valor):
                                símismo.dic['coefs'][p.nombre] = float(valor)
                if coef == 'Depredadores':
                    for d in símismo.depredadores_act:
                        if type(d) is Fase and \
                                (d.nombre not in símismo.dic['coefs'] or type(símismo.dic['coefs'][d.nombre]) is str):
                            valor = input('%s: Ingresar valor para depredador %s (%s): ' %
                                          (símismo.nombre, d.nombre,
                                           coefs[tipo_ecuaciones]['Depredadores']['a'] % d.nombre))
                            if len(valor):
                                símismo.dic['coefs'][d.nombre] = float(valor)
        if valor:
            guardar = input('¿Quieres guardar los coeficientes que entregaste para simulaciones futuras? (s/n)')
            if guardar == 's':
                símismo.escribir()

    def incr(símismo, paso, tipo_ecuaciones, estado_cultivo):

        símismo.cambio_pob = 0  # El cambio de población esta etapa de tiempo

        # Ecuaciones de mortalidad por deprededor
        def depredación(tipo):
            pred = 0
            if tipo == "LV":
                for depred in símismo.depredadores_act:
                    pred += depred.pob * símismo.dic["coefs"][depred.nombre]
                return pred
            elif tipo == "competitivo":  # Presas "compiten" para el tiempo de los depredadores
                for depred in símismo.depredadores_act:
                    comida_depred = 0
                    comida_crít_depred = depred.dic["coefs"]["comida_crít"] * depred.pob
                    for p in depred.presas_act:
                        if type(p) is Fase:  # Si la presa es un insecto
                            comida_depred += p.pob * depred.dic["coefs"][p.nombre]  # Consumo de presas
                        else:  # Sino, si la "presa" es un cultivo
                            comida_depred += estado_cultivo[p] * coefs[p]
                    if comida_depred > comida_crít_depred:  # Si hay demasiada comida
                        pred = (símismo.pob * depred.dic["coefs"][símismo.nombre])/comida_depred * \
                               comida_crít_depred * depred.pob
                    else:  # Si no hay demasiada comida
                        pred = depred.dic["coefs"][símismo.nombre] * depred.pob

                return pred
            else:
                return "Error en la calculación de la depredación."

        # Ecuaciones de crecimiento
        # Para ecuaciones Lotka-Voltera
        if tipo_ecuaciones == "Lotka-Voltera":
            r = 0
            if type(símismo.presas_act[0]) is Fase:  # si el insecto es un depredador
                for presa in símismo.presas_act:
                    r += presa.pob * símismo.dic["coefs"][presa.nombre]  # Consumo de presas
            elif type(símismo.presas_act[0]) is str:  # Si el insecto es un herbívoro
                r = símismo.dic["coefs"]["r"]
            símismo.cambio_pob = r * símismo.pob * paso

            símismo.cambio_pob -= depredación("LV") * paso

            símismo.cambio_pob -= símismo.pob * símismo.dic['coefs']['d'] * paso

        # Un tipo de ecuación con transición entre etapas de crecimiento del insecto
        elif tipo_ecuaciones == "etapas":
            # Crecimiento poblacional (por ejemplo, larvas aumentan por la eclosión de huevos). Notar que, a parte
            # del caso de un ciclo de vida simple, la fuente del crecimiento está externa a la fase actual y
            # "taza_crec" se refiere a la taza de conversión de la fase presente a la próxima fase.

            coefs = símismo.dic["coefs"]
            mortalidad = 0  # La mortalidad
            símismo.transición = 0  # La transición a la próxima etapa
            r = coefs["r"]

            # Una distribución triangular para calcular las transiciones de fases y la mortalidad natural
            # La distribución de población se pone a fecha con la conversión de individuos de la última fase
            símismo.hist_pob.append(símismo.dic["fuente"].transición)

            símismo.hist_pob = np.trim_zeros(símismo.hist_pob, "f")  # Quitar los 0s iniciales
            if not len(símismo.hist_pob):  # Si no queda nada, dejar un "0"
                símismo.hist_pob = [0]

            # Calcular transiciones de insectos a la próxima fase
            probs_trans = norm.cdf(list(range(len(símismo.hist_pob))),
                                   loc=coefs['trans_mu'], scale=coefs['trans_sigma'])
            probs_trans = np.insert(probs_trans, 0, [0])
            for día, pob in enumerate(reversed(símismo.hist_pob)):
                prob = (probs_trans[día+1] - probs_trans[día])/(1 - probs_trans[día])
                aleatorios = np.random.uniform(size=int(round(pob)))
                trans_cohorte = sum([i < prob for i in aleatorios])
                símismo.hist_pob[len(símismo.hist_pob) - día - 1] -= trans_cohorte
                símismo.transición += trans_cohorte
            símismo.transición *= paso

            # Mortalidad dependiente de la edad
            if "días_mort" in coefs.keys():
                probs_mort = norm.cdf(list(range(len(símismo.hist_pob))),
                                      loc=coefs['mort_mu'], scale=coefs['mort_sigma'])
                probs_mort = np.insert(probs_mort, 0, [0])
                for día, pob in enumerate(reversed(símismo.hist_pob)):
                    prob = (probs_mort[día+1] - probs_mort[día])/(1 - probs_mort[día])
                    aleatorios = np.random.uniform(size=int(round(pob)))
                    mort_cohorte = sum([i < prob for i in aleatorios])
                    símismo.hist_pob[len(símismo.hist_pob) - día - 1] -= mort_cohorte
                    mortalidad += mort_cohorte

            # Alternativamente, un factor de mortalidad constante
            elif "mortalidad" in coefs.keys():
                símismo.hist_pob = [x*(1-coefs["mortalidad"]) for x in símismo.hist_pob]
                mortalidad = símismo.pob * coefs["mortalidad"]

            # Reproducción dependiente de la edad
            reproducción = 0
            if "repr_mu" in coefs.keys():
                probs_repr = norm.cdf(list(range(len(símismo.hist_pob))),
                                      loc=coefs['mort_mu'], scale=coefs['mort_sigma'])
                probs_repr = np.insert(probs_repr, 0, [0])
                for día, pob in enumerate(reversed(símismo.hist_pob)):
                    prob = (probs_repr[día+1] - probs_repr[día])/(1 - probs_repr[día])
                    aleatorios = np.random.uniform(size=int(round(pob)))
                    reproducción += sum([i < prob for i in aleatorios]) * r

            elif "r" in coefs.keys():
                reproducción = r * (símismo.pob - mortalidad)

            # Mortalidad por falta de comida (unidades: fracción)
            mort_com = 0
            if len(símismo.presas_act):
                comida = 0
                comida_crít = coefs["comida_crít"] * (símismo.pob + símismo.dic["fuente"].transición)
                for presa in símismo.presas_act:
                    if type(presa) is Fase:  # Si la presa es un insecto
                        comida += presa.pob * coefs[presa.nombre]  # Consumo de presas
                    else:  # Sino, si la "presa" es un cultivo
                        comida += estado_cultivo[presa] * coefs[presa]
                if comida <= comida_crít:  # Si falta comida...
                    if comida_crít == 0:  # Para evitar división por 0 en lo que sigue
                        mort_com = 1
                    else:
                        mort_com = 1 - (comida/comida_crít)

            # Mortalidad por depredadores (unidades: fracción)
            mort_depred = depredación("competitivo")

            # Mortalidad total (unidades: insectos)
            mortalidad += (mort_depred + mort_com) * símismo.pob

            # Suponemos que la mortalidad no natural afecta todas las edades igualmente
            if sum(símismo.hist_pob):
                símismo.hist_pob = [x*(1-(mort_depred + mort_com)/sum(símismo.hist_pob)) for x in símismo.hist_pob]
                # Asegurar que no tenemos sub-poblaciones negativas
                símismo.hist_pob = [x*(x >= 0) for x in símismo.hist_pob]
                símismo.hist_pob = [round(x, 1) for x in símismo.hist_pob]

            # El cambio de población es la transición de la última fase, menos mortalidad y transiciones a nuevas fases
            símismo.cambio_pob = (- mortalidad - símismo.transición + símismo.dic["fuente"].transición) * paso
            # Añademos la reproducción a la transición a la próxima fase después del cálculo del cambio
            # en la población actual, porque la reproducción no sustraye de la población de una fase.
            símismo.transición += reproducción

        elif tipo_ecuaciones == "capacidad_de_carga":
            coefs = símismo.dic["coefs"]
            r = coefs["r"]
            K = 0
            for presa in símismo.presas_act:
                if type(símismo.presas_act[0]) is Fase:  # Si el insecto es un depredador,
                    K += presa.pob * coefs[presa.nombre]  # el consumo de presas aumenta K.
                elif type(símismo.presas_act[0]) is str:  # Y si el insecto es un herbívoro,
                    K += coefs[presa] * estado_cultivo[presa]  # K se determina por el estado del cultivo.
            if K > 0:  # Evitar dividir por 0 en la ecuación dN/dt = rN(K-N)/K
                símismo.cambio_pob = r * símismo.pob * (K - símismo.pob)/K * paso
            else:
                símismo.cambio_pob = -símismo.pob

            # Muertes por depredación determinadas por el modelo competitivo
            if len(símismo.depredadores_act):
                símismo.cambio_pob -= depredación("competitivo") * paso

        else:
            print("Tipo de ecuación no reconocido.")

    def actualizar(símismo):

        # Implementar los cambios de poblaciones
        símismo.pob += símismo.cambio_pob
        símismo.cambio_pob = 0

        # Añadir fluctuaciones naturales a la población. ToDO: poner SIGMA como coeficiente del insecto
        símismo.pob = np.random.normal(símismo.pob, 1)
        símismo.pob = round(símismo.pob, 0)  # No sirve para nada 1 * 10^-18 de una avispa

        # Asegurarnos que, después de todas estas acrobacias matemáticas, no terminamos con menos de 0 insectos.
        if símismo.pob < 0:
            símismo.pob = 0
