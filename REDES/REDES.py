import os
import numpy as np
import matplotlib.pylab as dib

from COSO import Coso
from REDES.INSECTOS import Insecto
from INCERT.CALIB import genmodbayes, calib, guardar
from INCERT.INCERT import anal_incert
#dib.switch_backend('cairo')


# Esta clase representa una red agroecológica
class Red(Coso):
    def __init__(símismo, nombre, insectos):
        # insectos debe ser una lista de los objectos de insectos

        # El diccionario de los datos para cada red
        dic = dict(Insectos={}, tipo_ecuaciones="")
        for i in insectos:
            dic['Insectos'][i.nombre] = i

        # Esta clase se initializa como describido en Coso
        super().__init__(nombre=nombre, ext='red', dic=dic, directorio=os.path.join('Personales', 'Redes', nombre))

        símismo.insectos = {}
        símismo.objetos = dict(insectos=símismo.insectos)

        símismo.poblaciones = {}
        símismo.inicializado = False
        símismo.datos = {}
        símismo.pobs_inic = {}

    def ejec(símismo, poblaciones_iniciales=None):
        # poblaciones_iniciales debe ser un diccionario del formato {'insecto1': {'fase1': pob, 'fase2': pob}, etc.}

        for insecto in símismo.dic["Insectos"]:  # Migrar los insectos del diccionario al objeto si mismo
            símismo.insectos[insecto] = Insecto(símismo.dic["Insectos"][insecto])
        for insecto in símismo.insectos:  # Inicializar las instancias de los insectos
            símismo.insectos[insecto].ejec(otros_insectos=símismo.dic["Insectos"])
            # Para guardar los datos de poblaciones (para pruebas del modelo)
            símismo.poblaciones[insecto] = {}
            for fase in símismo.insectos[insecto].fases:
                símismo.poblaciones[insecto][fase] = []

        # Inicializar las poblaciones
        if not poblaciones_iniciales:
            if len(símismo.datos):
                datos = símismo.datos
                for insecto in datos:
                    poblaciones_iniciales[insecto] = {}
                    for fase in datos[insecto]:
                        poblaciones_iniciales[insecto][fase] = datos[insecto][fase][0]
            else:
                return 'Faltan datos iniciales.'
        símismo.pobs_inic = poblaciones_iniciales

        for insecto in símismo.pobs_inic:
            if insecto in símismo.insectos:
                # Si se te olvidó especificar la fase de la población del insecto:
                if type(símismo.pobs_inic[insecto]) is float or type(símismo.pobs_inic[insecto]) is int:
                    print('Cuidado: no se especificó la fase para la población inical del insecto %s.' % insecto)
                    fase = list(símismo.insectos[insecto].fases.keys())[0]  # escoger uno al hazar
                    símismo.insectos[insecto].fases[fase].pob = símismo.pobs_inic[insecto]
                    símismo.insectos[insecto].fases[fase].hist_pob = [símismo.pobs_inic[insecto]]
                    # Inicializar los datos de poblaciones de la red
                    símismo.poblaciones[insecto][fase] = [símismo.pobs_inic[insecto]]
                else:  # Si no se te olvidó nada
                    for fase in símismo.pobs_inic[insecto]:
                        if fase in símismo.insectos[insecto].fases:
                            # Inicializar la población del insecto
                            símismo.insectos[insecto].fases[fase].pob = símismo.pobs_inic[insecto][fase]
                            símismo.insectos[insecto].fases[fase].hist_pob = [símismo.pobs_inic[insecto][fase]]
                            # Inicializar los datos de poblaciones de la red
                            símismo.poblaciones[insecto][fase] = [símismo.pobs_inic[insecto][fase]]
        símismo.inicializado = True  # Marcar la red como inicializada

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
    def simul(símismo, tiempo_final, tiempo_inic=0, pobs_inic=None, estado_cultivo=1000000, paso=1, rep=10):
        print('Simulando...')
        if not pobs_inic:
            pobs_inic = símismo.pobs_inic

        # Correr las simulaciones
        for j in range(rep):
            símismo.borrar(poblaciones_iniciales=pobs_inic)
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

        símismo.dibujar(poblaciones=poblaciones)
        return poblaciones

    # Una función para borar los datos de simulación (guardando solamente el primer dato, o población inicial)
    def borrar(símismo, poblaciones_iniciales):
        if símismo.inicializado and poblaciones_iniciales:
            for insecto in poblaciones_iniciales:
                for fase in poblaciones_iniciales[insecto]:
                    if insecto in símismo.insectos:
                        símismo.insectos[insecto].fases[fase].pob = poblaciones_iniciales[insecto][fase]
                        símismo.insectos[insecto].fases[fase].hist_pob = [poblaciones_iniciales[insecto][fase]]
                        símismo.poblaciones[insecto][fase] = [poblaciones_iniciales[insecto][fase]]
        else:
            símismo.ejec(poblaciones_iniciales)

    def dibujar(símismo, insectos=None, datos_obs=None, poblaciones=None):
        print('Dibujando...')
        if insectos is None:  # Si no se especificaron insectos, utilizar todos los insectos de la red.
            insectos = list(símismo.insectos.keys())

        if poblaciones is None:
            poblaciones = símismo.poblaciones

        for núm, nombre in enumerate(insectos):
            print(nombre)
            colores = ("red", "orange", "yellow", "green", "blue", "purple", "fuchsia", "black")

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

                if datos_obs:  # Si hay datos observados disponibles, incluirlos como puntos abiertos
                    sub[núm_fase, 0].plot(datos_obs[nombre][fase], "o", color=colores[núm_color])

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

    def calibrar(símismo, iteraciones=500, quema=100, espacio=1, dibujar=True):
        modelo = genmodbayes(símismo.datos, símismo.dic, símismo.simul)
        calibrado = calib(modelo, it=iteraciones, quema=quema, espacio=espacio)
        guardar(calibrado, símismo.dic_incert)

        porcent, resultados_incert = anal_incert(símismo.dic_incert, símismo.simul, símismo.datos)

        if dibujar:
            símismo.dibujar(datos_obs=símismo.datos, poblaciones=resultados_incert)

        # Devolver el % de observaciones que caen en el intervalo de 95% de confianza
        return porcent
