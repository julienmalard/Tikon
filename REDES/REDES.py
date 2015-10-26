import os
import numpy as np
import matplotlib.pylab as dib

from COSO import Coso
dib.switch_backend('cairo')


# Esta clase representa una red agroecológica
class Red(Coso):
    def __init__(símismo, nombre, insectos, poblaciones_iniciales=None):
        # insectos debe ser una lista de los objectos de insectos

        # El diccionario de los datos para cada red
        símismo.dic = dict(Insectos={}, tipo_ecuaciones="")
        for i in insectos:
            símismo.dic['Insectos'][i.nombre] = i

        # Esta clase se initializa como describido en Coso
        super().__init__(nombre=nombre, ext='red', directorio=os.path.join('Personales', 'Redes'))

        símismo.insectos = {}
        símismo.poblaciones = {}
        símismo.inicializado = False
        símismo.pobs_inic = poblaciones_iniciales

    def ejec(símismo, poblaciones_iniciales):
        # poblaciones_iniciales debe ser un diccionario del formato {'insecto1': {'fase1': pob, 'fase2': pob}, etc.}

        for insecto in símismo.dic["Insectos"]:  # Migrar los insectos del diccionario al objeto si mismo
            símismo.insectos[insecto] = símismo.dic["Insectos"][insecto]
        for insecto in símismo.insectos:  # Inicializar las instancias de los insectos
            símismo.insectos[insecto].ejec(otros_insectos=símismo.dic["Insectos"])
            # Para guardar los datos de poblaciones (para pruebas del modelo)
            símismo.poblaciones[insecto] = {}
            for fase in símismo.insectos[insecto].fases:
                símismo.poblaciones[insecto][fase] = []

        # Inicializar las poblaciones
        if not poblaciones_iniciales:
            poblaciones_iniciales = símismo.pobs_inic
        else:
            símismo.pobs_inic = poblaciones_iniciales

        for insecto in poblaciones_iniciales:
            if insecto in símismo.insectos:
                # Si se te olvidó especificar la fase de la población del insecto:
                if type(poblaciones_iniciales[insecto]) is float or type(poblaciones_iniciales[insecto]) is int:
                    print('Cuidado: no se especificó la fase para la población inical del insecto %s.' % insecto)
                    fase = list(símismo.insectos[insecto].fases.keys())[0]  # escoger uno al hazar
                    símismo.insectos[insecto].fases[fase].pob = poblaciones_iniciales[insecto]
                    símismo.insectos[insecto].fases[fase].hist_pob = [poblaciones_iniciales[insecto]]
                    # Inicializar los datos de poblaciones de la red
                    símismo.poblaciones[insecto][fase] = [poblaciones_iniciales[insecto]]
                else:  # Si no se te olvidó nada
                    for fase in poblaciones_iniciales[insecto]:
                        if fase in símismo.insectos[insecto].fases:
                            # Inicializar la población del insecto
                            símismo.insectos[insecto].fases[fase].pob = poblaciones_iniciales[insecto][fase]
                            símismo.insectos[insecto].fases[fase].hist_pob = [poblaciones_iniciales[insecto][fase]]
                            # Inicializar los datos de poblaciones de la red
                            símismo.poblaciones[insecto][fase] = [poblaciones_iniciales[insecto][fase]]
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
    def simul(símismo, paso, estado_cultivo, tiempo_final, tiempo_inic=0, pobs_inic=None, rep=10):
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
                if type(poblaciones[nombre][fase]) is np.ndarray:
                    promedios = np.mean(poblaciones[nombre][fase], axis=0)
                    máx = np.max(poblaciones[nombre][fase], axis=0)
                    mín = np.min(poblaciones[nombre][fase], axis=0)
                else:
                    promedios = poblaciones[nombre][fase]
                    máx = mín = None

                x = np.array(range(len(promedios)))
                y = promedios
                sub[núm_fase, 0].plot(x, y, lw=2, color=colores[núm])

                if máx is not None and mín is not None:
                    sub[núm_fase, 0].fill_between(x, máx, mín, facecolor=colores[núm], alpha=0.5)
                if núm_fase == 0:
                    sub[núm_fase, 0].set_xlabel('Día')
                else:
                    for label in sub[núm_fase, 0].get_yticklabels():
                        label.set_visible(False)

                sub[núm_fase, 0].set_ylabel('Población %s' % fase)

                if datos_obs:  # Si hay datos observados disponibles, incluirlos como puntos abiertos
                    sub[núm_fase, 0].plot(datos_obs[nombre][fase], "o", color=colores[núm])

            fig.suptitle(nombre)
            fig.savefig(os.path.join(símismo.directorio, "Tikon_%s_%s.png" % (símismo.nombre, nombre)))
            # pylab.savefig("Tikon_%s_%s.png" % (símismo.nombre, nombre))
