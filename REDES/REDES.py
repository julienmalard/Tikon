import os
import numpy as np
import pylab

from COSO import Coso


# Esta clase representa una red agroecológica
class Red(Coso):
    def __init__(símismo, nombre, insectos, poblaciones_iniciales=None):
        # insectos debe ser una lista de los objectos de insectos

        # El diccionario de los datos para cada red
        símismo.dic = dict(Insectos={}, tipo_ecuaciones="")
        for i in insectos:
            símismo.dic['Insectos'][i.nombre] = i

        # Esta clase se initializa como describido en Coso
        super().__init__(nombre=nombre, ext='red', directorio=os.path.join('Proyectos', 'Personales', 'Redes'))

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
    def simul(símismo, paso, estado_cultivo, tiempo_final, tiempo_inic=0, pobs_inic=None):
        print('Simulando...')
        if not pobs_inic:
            pobs_inic = símismo.pobs_inic
        símismo.borrar(poblaciones_iniciales=pobs_inic)
        for i in range(tiempo_inic, tiempo_final, paso):
            símismo.incr(paso, estado_cultivo=estado_cultivo)
        símismo.dibujar()
        return símismo.poblaciones

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

    def dibujar(símismo, insectos=None, datos_obs=None):
        print('Dibujando...')
        if insectos is None:  # Si no se especificaron insectos, utilizar todos los insectos de la red.
            insectos = list(símismo.insectos.keys())

        for núm, nombre in enumerate(insectos):
            print(nombre)
            colores = ("red", "orange", "yellow", "green", "blue", "purple", "fuchsia", "black")
            # pylab.figure(1 + núm)  # Un gráfico por insecto (con todas las fases en sub-gráficos)
            # pylab.subplots_adjust(hspace=0, right=1)  # Se me olvidó qué hace esta línea...
            for núm_fase, fase in enumerate(símismo.insectos[nombre].fases):
                x = np.array(range(len(símismo.poblaciones[nombre][fase])))
                y = np.array(símismo.poblaciones[nombre][fase])
                pylab.plot(x, y)
                pylab.title(símismo.poblaciones[nombre] + ' ' + símismo.poblaciones[nombre][fase])
                pylab.xlabel('Días')
                pylab.ylabel('Población')
                pylab.show()
                # print(núm_fase, fase)
                # print(símismo.poblaciones[nombre][fase])
                # máx_x = len(símismo.poblaciones[nombre][fase])
                # pylab.subplot(máx_x, 1, núm_fase + 1)
                # pylab.title = símismo.nombre + " " + nombre
                # if datos_obs:  # Si hay datos observados disponibles, incluirlos como puntos abiertos
                #     pylab.plot(datos_obs[nombre][fase], "o", color=colores[núm_fase])
                # # Añadir una línea para representar las predicciones
                # pylab.plot(símismo.poblaciones[nombre][fase], color=colores[núm_fase],
                #            linewidth=2)
                # pylab.ylabel(fase)
                # pylab.xticks = (range(0, int(máx_x*1.1), int(máx_x/10)))
                # pylab.xlabel('Días')
               # pylab.savefig("Tikon_%s_%s.png" % (símismo.nombre, nombre))
