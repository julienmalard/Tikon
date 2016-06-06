import os
import numpy as np
import matplotlib.pylab as dib

from Controles import directorio_base
from COSO import Simulable
from RAE.INSECTOS import Insecto
from MATEMÁTICAS.CALIB import genmodbayes, calib, guardar
from MATEMÁTICAS.INCERT import anal_incert
# dib.switch_backend('cairo')


# Esta clase representa una red agroecológica
class Red(Simulable):
    def __init__(símismo, nombre, insectos, cultivos, insectos_compartidos=False):
        """

        :param nombre: el nombre de la red (carácter)
        :param insectos: lista de los nombres de los insectos
        :return: nada
        """

        # El diccionario de los datos para cada red
        dic = dict(Insectos=insectos, Cultivos=cultivos, tipo_ecuaciones="")

        # Esta clase se initializa como describido en Coso
        super().__init__(nombre=nombre, ext='red', dic=dic, directorio=os.path.join('Redes', nombre))

        símismo.insectos = {}
        símismo.objetos = dict(insectos=símismo.insectos)

        for insecto in símismo.dic["Insectos"]:  # Migrar los insectos del diccionario al objeto si mismo
            if not insectos_compartidos:
                insectos_exist_red = os.listdir(símismo.directorio)
                # Buscar en el directorio de la red
                if insecto in insectos_exist_red:
                    símismo.insectos[insecto] = Insecto(insecto, directorio=os.path.join(símismo.nombre, insecto))
                    continue
                else:
                    print('Aviso: no hay insecto guardado en red %s para insecto %s. Buscando en el directorio '
                          'general.' % (símismo.nombre, insecto))
            # Si no lo encontramos, o si estamos utilizando los insectos comunes, buscar en el lugar comun:
            insectos_exist_comunes = os.listdir(os.path.join(directorio_base, 'Proyectos', 'Redes'))
            if insecto in insectos_exist_comunes:
                símismo.insectos[insecto] = Insecto(insecto, directorio=os.path.join(símismo.nombre, insecto),
                                                    fuente=os.path.join(directorio_base,
                                                                        'Proyectos', 'Redes', insecto)
                                                    )
            else:
                print('No hay archivo para insecto %s. Creando insecto nuevo.' % símismo.nombre)
                huevo = input('¿Incluyemos la fase huevo del insecto en el modelo? (s/n)')
                njuvenil = input('¿Cuántas fases juveniles del insecto hay que incluir?')
                pupa = input('¿Incluyemos la fase pupa del insecto en el modelo? (s/n)')
                adulto = input('¿Incluyemos la fase adulta del insecto en el modelo? (s/n)')
                tipo_ecuaciones = input('¿Qué tipo de ecuación utilizar para modelizar al insecto?')
                símismo.insectos[insecto] = Insecto(insecto, huevo=huevo, njuvenil=njuvenil, pupa=pupa, adulto=adulto,
                                                    tipo_ecuaciones=tipo_ecuaciones,
                                                    directorio=os.path.join(símismo.nombre, insecto))

        símismo.poblaciones = {}
        símismo.datos = {}
        símismo.vals_inic = {}

    def ejec(símismo, poblaciones_iniciales=None):
        # poblaciones_iniciales debe ser un diccionario del formato {'insecto1': {'fase1': pob, 'fase2': pob}, etc.}

        for insecto in símismo.insectos:  # Inicializar las instancias de los insectos
            símismo.insectos[insecto].ejec(otros_insectos=símismo.insectos, cultivos=símismo.dic['Cultivos'])

        símismo.inic_pobs(poblaciones_iniciales)

    def inic_pobs(símismo, poblaciones_iniciales):

        # Para guardar los datos de poblaciones (para corridas independientes del modelo RAE)
        for insecto in símismo.insectos:
            símismo.poblaciones[insecto] = {}
            for fase in símismo.insectos[insecto].fases:
                símismo.poblaciones[insecto][fase] = []

        # Inicializar las poblaciones
        if poblaciones_iniciales is None:
            if len(símismo.datos):
                poblaciones_iniciales = símismo.datos
            else:
                raise ValueError('Faltan datos iniciales.')

        for insecto in poblaciones_iniciales:
            for fase in poblaciones_iniciales[insecto]:
                pob = poblaciones_iniciales[insecto][fase]
                if type(pob) is list:
                    poblaciones_iniciales[insecto][fase] = pob[0]
                    pob = poblaciones_iniciales[insecto][fase]
                if type(pob) is tuple:
                    poblaciones_iniciales[insecto][fase] = pob[1]

        símismo.vals_inic = poblaciones_iniciales

        for insecto in símismo.vals_inic:
            for fase in símismo.vals_inic[insecto]:
                if insecto in símismo.insectos:
                    pob = símismo.vals_inic[insecto][fase]
                    símismo.insectos[insecto].fases[fase].pob = pob
                    símismo.insectos[insecto].fases[fase].hist_pob = [pob]
                    símismo.poblaciones[insecto][fase] = [pob]

    def incr(símismo, paso, estado_cultivo):
        poblaciones = {}  # Para comunicación con el submódulo PARCELA
        for insecto in símismo.insectos:
            símismo.insectos[insecto].incr(paso, estado_cultivo)

        for insecto in símismo.insectos:
            símismo.insectos[insecto].actualizar()
            poblaciones[insecto] = símismo.insectos[insecto].pob  # Para comunicación con el submódulo PARCELA
            for fase in símismo.insectos[insecto].pob:
                if fase in símismo.poblaciones[insecto].keys():
                    símismo.poblaciones[insecto][fase].append(símismo.insectos[insecto].pob[fase])
        return poblaciones  # Para comunicación con el submódulo PARCELA

    # Una funcción para simular las plagas en isolación del cultivo (estado del cultivo es un constante exógeno)
    def simul(símismo, tiempo_final, estado_cultivo, tiempo_inic=0, vals_inic=None, paso=1, rep=100, dibujar=True):
        if not vals_inic:
            vals_inic = símismo.vals_inic

        # Correr las simulaciones
        for j in range(rep):
            símismo.inic_pobs(poblaciones_iniciales=vals_inic)
            for i in range(tiempo_inic, tiempo_final, paso):
                símismo.incr(paso, estado_cultivo=estado_cultivo)

            # Guardar los resultados
            if j == 0:
                # Iniciar el diccionario para guardar datos de poblaciones de varias repeticiones
                poblaciones = {}
                for insecto in símismo.poblaciones:
                    poblaciones[insecto] = {}
                    for fase in símismo.poblaciones[insecto]:
                        poblaciones[insecto][fase] = símismo.poblaciones[insecto][fase]
            else:
                for insecto in símismo.poblaciones:
                    for fase in símismo.poblaciones[insecto]:
                        poblaciones[insecto][fase] = np.vstack((poblaciones[insecto][fase],
                                                                símismo.poblaciones[insecto][fase]))

        if dibujar:
            símismo.dibujar(poblaciones=poblaciones)
        return poblaciones

    # Asegurarse de que guardar la red también guarda los datos de sus insectos
    def guardar(símismo, documento=''):
        # Primero, guardar la red sí misma...
        super().guardar(documento)
        # ...y guardar todos sus insectos también
        for insecto in símismo.insectos:
            símismo.insectos[insecto].guardar(documento)

    # Una función para guardar los insectos de la red en el área común para que lo pueda acceder otras redes
    def guardar_común(símismo):
        for insecto in símismo.insectos:
            símismo.insectos[insecto].guardar(documento=os.path.join(directorio_base, 'Proyectos', 'Redes'))

    def dibujar(símismo, insectos=None, datos_obs=None, poblaciones=None):
        if insectos is None:  # Si no se especificaron insectos, utilizar todos los insectos de la red.
            insectos = list(símismo.insectos.keys())

        if poblaciones is None:
            poblaciones = símismo.poblaciones

        for núm, nombre in enumerate(insectos):
            colores = ("red", "orange", "green", "blue", "purple", "fuchsia", "black")

            # Un gráfico por insecto (con todas las fases en sub-gráficos). El 'squeeze' es necesario.
            fig, sub = dib.subplots(len(poblaciones[nombre].keys()), 1, sharex=True, sharey=True, squeeze=False)

            for núm_fase, fase in enumerate(poblaciones[nombre]):
                # Si tenemos una matriz mltidimensional (con más que una corrida):
                if type(poblaciones[nombre][fase]) is np.ndarray:
                    promedios = np.mean(poblaciones[nombre][fase], axis=0)
                    máx = np.max(poblaciones[nombre][fase], axis=0)
                    mín = np.min(poblaciones[nombre][fase], axis=0)
                else:  # Si solo tenemos una corrida, no calcular máximo y mínimo
                    promedios = poblaciones[nombre][fase]
                    máx = mín = None

                x = np.array(range(len(promedios)))
                y = promedios

                núm_color = núm % len(colores)  # Para que nunca falten colores
                sub[núm_fase, 0].plot(x, y, lw=2, color=colores[núm_color])

                if máx is not None and mín is not None:
                    sub[núm_fase, 0].fill_between(x, máx, mín, facecolor=colores[núm_color], alpha=0.5)
                if núm_fase == 0:
                    sub[núm_fase, 0].set_xlabel('Día')
                else:
                    for label in sub[núm_fase, 0].get_yticklabels():
                        label.set_visible(False)

                sub[núm_fase, 0].set_ylabel('Población %s' % fase)

                if datos_obs:  # Si hay datos observados disponibles, incluirlos como puntos
                    sub[núm_fase, 0].plot(datos_obs[nombre][fase][0], datos_obs[nombre][fase][1],
                                          "o", color=colores[núm_color])

            fig.suptitle(nombre)
            fig.savefig(os.path.join(símismo.directorio, "Tikon_%s_%s.png" % (símismo.nombre, nombre)))

    def cargardatos(símismo, documento):
        with open(documento) as d:
            doc = d.readlines()
        variables = doc[0].replace(';', ',').split(',')
        col_tiempo = 0

        símismo.datos = {}
        for i in variables[1:]:
            insecto = i.split('_')[0]
            if len(i.split('_')) == 1:
                fase = i.split('_')[1]
            else:
                fase = 'adulto'
            if insecto not in símismo.datos.keys():
                símismo.datos[insecto] = {}
            símismo.datos[insecto][fase] = []

        for n, l in enumerate(doc[1:]):
            texto = l.replace(';', ',').split(',')

            for m, i in enumerate(texto[1:]):
                if len(i) and i != -99:  # Si hay un dato de este insecto para el día
                    insecto = variables[m+1].split('_')[0]
                    fase = variables[m+1].split('_')[1]
                    símismo.datos[insecto][fase][0].append(float(texto[col_tiempo]))
                    símismo.datos[insecto][fase][1].append(float(i))

    def calibrar(símismo, estado_cultivo, iteraciones=10000, quema=100, espacio=10, dibujar=True):
        opciones_simul = dict(estado_cultivo=estado_cultivo, rep=1, dibujar=False)
        modelo = genmodbayes(símismo, opciones_simul)
        calibrado = calib(modelo, it=iteraciones, quema=quema, espacio=espacio)
        guardar(calibrado, símismo)

        print(símismo.vals_inic)
        porcent, resultados_incert = anal_incert(símismo, opciones_simul)

        if dibujar:
            for n, corrida in enumerate(resultados_incert):
                nombre_corrida = list(símismo.datos.keys())[n]
                símismo.dibujar(datos_obs=símismo.datos[nombre_corrida], poblaciones=corrida)

        # Devolver el % de observaciones que caen en el intervalo de 95% de confianza
        return porcent
