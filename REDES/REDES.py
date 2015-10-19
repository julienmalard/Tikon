from COSO import Coso
from REDES.INSECTOS import Insecto


# Esta clase representa una red agroecológica
class Red(Coso):
    def __init__(símismo, *args, **kwargs):
        # El diccionario de los datos para cada red
        símismo.dic_base = dict(Insectos=[], tipo_ecuaciones="")
        símismo.ext = "red"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        super().__init__(*args, **kwargs)  # Esta clase se initializa como describido en Coso
        símismo.insectos = {}
        símismo.tipo_ecuaciones = símismo.dic["tipo_ecuaciones"]
        símismo.poblaciones = {}
        símismo.inicializado = False

    def ejec(símismo, poblaciones_iniciales=()):
        símismo.tipo_ecuaciones = símismo.dic["tipo_ecuaciones"]
        for insecto in símismo.dic["Insectos"]:  # Migrar los insectos del diccionario al objeto si mismo
            símismo.insectos[insecto] = símismo.dic["Insectos"][insecto]
        for insecto in símismo.insectos:  # Crear las instancias de los insectos
            símismo.insectos[insecto].ejec(otros_insectos=símismo.dic["Insectos"])
            # Para guardar los datos de poblaciones (para pruebas del modelo)
            símismo.poblaciones[insecto] = {}
            for fase in símismo.insectos[insecto].fases:
                símismo.poblaciones[insecto][fase] = []
        if len(poblaciones_iniciales):
            for insecto in poblaciones_iniciales:  # Inicializar las poblaciones
                if insecto in símismo.insectos.keys():
                    for fase in poblaciones_iniciales[insecto]:
                        # Inicializar la población del insecto
                        símismo.insectos[insecto].fases[fase].pob = poblaciones_iniciales[insecto][fase]
                        símismo.insectos[insecto].fases[fase].hist_pob = [poblaciones_iniciales[insecto][fase]]
                        # Inicializar los datos de poblaciones de la red
                        símismo.poblaciones[insecto][fase] = [poblaciones_iniciales[insecto][fase]]
        símismo.inicializado = True

    def incr(símismo, paso, estado_cultivo):
        poblaciones = {}  # Para comunicación con el submódulo PARCELA
        for insecto in símismo.insectos:
            símismo.insectos[insecto].incr(paso, símismo.tipo_ecuaciones, estado_cultivo)

        for insecto in símismo.insectos:
            símismo.insectos[insecto].actualizar()
            poblaciones[insecto] = símismo.insectos[insecto].pob  # Para comunicación con el submódulo PARCELA
            for fase in símismo.insectos[insecto].pob:
                if fase in símismo.poblaciones[insecto].keys():
                    símismo.poblaciones[insecto][fase].append(símismo.insectos[insecto].pob[fase])
        return poblaciones  # Para comunicación con el submódulo PARCELA

    # Una funcción para simular las plagas en isolación del cultivo (estado del cultivo es un constante exógeno)
    def simul(símismo, paso, pob_inic, estado_cultivo, tiempo_final, tiempo_inic=0):
        símismo.borrar(poblaciones_iniciales=pob_inic)
        for i in range(tiempo_inic, tiempo_final, paso):
            símismo.incr(paso, estado_cultivo=estado_cultivo)
        return símismo.poblaciones

    # Una función para borar los datos de simulación (guardando solamente el primer dato, o población inicial)
    def borrar(símismo, poblaciones_iniciales):
        if símismo.inicializado:
            for insecto in poblaciones_iniciales:
                for fase in poblaciones_iniciales[insecto]:
                    if insecto in símismo.insectos:
                        símismo.insectos[insecto].fases[fase].pob = poblaciones_iniciales[insecto][fase]
                        símismo.insectos[insecto].fases[fase].hist_pob = [poblaciones_iniciales[insecto][fase]]
                        símismo.poblaciones[insecto][fase] = [poblaciones_iniciales[insecto][fase]]
        else:
            símismo.ejec(poblaciones_iniciales)

    def dibujar(símismo, insectos=None, datos_obs = None):
        print("dibujar")
        import pylab
        if insectos is None:  # Si no se especificaron insectos, utilizar todos los insectos de la red.
            insectos = símismo.insectos

        for núm, nombre in enumerate(insectos):
            print(nombre)
            colores = ("red", "orange", "yellow", "green", "blue", "purple", "fuchsia", "black")
            pylab.figure(1 + núm)  # Un gráfico por insecto (con todas las fases en sub-gráficos)
            pylab.subplots_adjust(hspace=0, right=1)  # Se me olvidó qué hace esta línea...
            for núm_fase, fase in enumerate(símismo.insectos[nombre].fases):
                print(fase)
                máx_x = len(símismo.poblaciones[nombre][fase])
                pylab.subplot(máx_x, 1, núm_fase + 1)
                pylab.title = símismo.nombre + " " + nombre
                if datos_obs:  # Si hay datos observados disponibles, incluirlos como puntos abiertos
                    pylab.plot(datos_obs[nombre][fase], "o", color=colores[núm_fase])
                # Añadir una línea para representar las predicciones
                pylab.plot(símismo.poblaciones[nombre][fase], color=colores[núm_fase],
                           linewidth=2)
                pylab.ylabel(fase)
                pylab.xticks = (range(0, int(máx_x*1.1), int(máx_x/10)))
                pylab.xlabel('Días')
                pylab.savefig("Tikon_" + nombre + ".png")
