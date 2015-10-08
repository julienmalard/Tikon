from COSO import Coso
from PLAGAS.INSECTOS import Insecto


# Esta clase representa una red agroecológica
class Red(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada red
        simismo.dic_base = dict(Insectos=[], tipo_ecuaciones="")
        simismo.ext = "red"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        super().__init__(*args, **kwargs)  # Esta clase se initializa como describido en Coso
        simismo.insectos = {}
        simismo.tipo_ecuaciones = simismo.dic["tipo_ecuaciones"]
        simismo.poblaciones = {}
        simismo.inicializado = False

    def ejec(simismo, poblaciones_iniciales=()):
        simismo.tipo_ecuaciones = simismo.dic["tipo_ecuaciones"]
        for insecto in simismo.dic["Insectos"]:  # Migrar los insectos del diccionario al objeto si mismo
            simismo.insectos[insecto] = simismo.dic["Insectos"][insecto]
        for insecto in simismo.insectos:  # Crear las instancias de los insectos
            simismo.insectos[insecto].ejec(otros_insectos=simismo.dic["Insectos"])
            # Para guardar los datos de poblaciones (para pruebas del modelo)
            simismo.poblaciones[insecto] = {}
            for fase in simismo.insectos[insecto].fases:
                simismo.poblaciones[insecto][fase] = []
        if len(poblaciones_iniciales):
            for insecto in poblaciones_iniciales:  # Inicializar las poblaciones
                if insecto in simismo.insectos.keys():
                    for fase in poblaciones_iniciales[insecto]:
                        # Inicializar la población del insecto
                        simismo.insectos[insecto].fases[fase].pob = poblaciones_iniciales[insecto][fase]
                        simismo.insectos[insecto].fases[fase].hist_pob = [poblaciones_iniciales[insecto][fase]]
                        # Inicializar los datos de poblaciones de la red
                        simismo.poblaciones[insecto][fase] = [poblaciones_iniciales[insecto][fase]]
        simismo.inicializado = True

    def incr(simismo, paso, estado_cultivo):
        poblaciones = {}  # Para comunicación con el submódulo PARCELA
        for insecto in simismo.insectos:
            simismo.insectos[insecto].incr(paso, simismo.tipo_ecuaciones, estado_cultivo)

        for insecto in simismo.insectos:
            simismo.insectos[insecto].actualizar()
            poblaciones[insecto] = simismo.insectos[insecto].pob  # Para comunicación con el submódulo PARCELA
            for fase in simismo.insectos[insecto].pob:
                if fase in simismo.poblaciones[insecto].keys():
                    simismo.poblaciones[insecto][fase].append(simismo.insectos[insecto].pob[fase])
        return poblaciones  # Para comunicación con el submódulo PARCELA

    # Una funcción para simular las plagas en isolación del cultivo (estado del cultivo es un constante exógeno)
    def simul(simismo, paso, pob_inic, estado_cultivo, tiempo_final, tiempo_inic=0):
        simismo.borrar(poblaciones_iniciales=pob_inic)
        for i in range(tiempo_inic, tiempo_final, paso):
            simismo.incr(paso, estado_cultivo=estado_cultivo)
        return simismo.poblaciones

    # Una función para borar los datos de simulación (guardando solamente el primer dato, o población inicial)
    def borrar(simismo, poblaciones_iniciales):
        if simismo.inicializado:
            for insecto in poblaciones_iniciales:
                for fase in poblaciones_iniciales[insecto]:
                    if insecto in simismo.insectos:
                        simismo.insectos[insecto].fases[fase].pob = poblaciones_iniciales[insecto][fase]
                        simismo.insectos[insecto].fases[fase].hist_pob = [poblaciones_iniciales[insecto][fase]]
                        simismo.poblaciones[insecto][fase] = [poblaciones_iniciales[insecto][fase]]
        else:
            simismo.ejec(poblaciones_iniciales)

    def dibujar(simismo, insectos=None, datos_obs = None):
        print("dibujar")
        import pylab
        if insectos is None:  # Si no se especificaron insectos, utilizar todos los insectos de la red.
            insectos = simismo.insectos

        for núm, nombre in enumerate(insectos):
            print(nombre)
            colores = ("red", "orange", "yellow", "green", "blue", "purple", "fuchsia", "black")
            pylab.figure(1 + núm)  # Un gráfico por insecto (con todas las fases en sub-gráficos)
            pylab.subplots_adjust(hspace=0, right=1)  # Se me olvidó qué hace esta línea...
            for núm_fase, fase in enumerate(simismo.insectos[nombre].fases):
                print(fase)
                máx_x = len(simismo.poblaciones[nombre][fase])
                pylab.subplot(máx_x, 1, núm_fase + 1)
                pylab.title = simismo.nombre + " " + nombre
                if datos_obs:  # Si hay datos observados disponibles, incluirlos como puntos abiertos
                    pylab.plot(datos_obs[nombre][fase], "o", color=colores[núm_fase])
                # Añadir una línea para representar las predicciones
                pylab.plot(simismo.poblaciones[nombre][fase], color=colores[núm_fase],
                           linewidth=2)
                pylab.ylabel(fase)
                pylab.xticks = (range(0, int(máx_x*1.1), int(máx_x/10)))
                pylab.xlabel('Días')
                pylab.savefig("Tikon_" + nombre + ".png")
