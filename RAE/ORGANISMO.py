from NuevoCOSO import Coso
import RAE.Ecuaciones as Ec


class Organismo(Coso):

    # La extensión de base para organismos
    ext = '.org'

    def __init__(símismo, nombre=None, fuente=None):
        """
        Esta clase representa cualquier organismo vivo en una red agroecológica. Esta clase se llama directamente muy
          rara vez, porque se llama más facilmente por el uso de una de sus subclases (Insecto, Enfermedad, etc.) o de
          subclases.

        :param nombre: El nombre del organismo
        :type nombre: str

        :param fuente: Un archivo de organismo guardada (opcional) para cargar.
        :type fuente: str

        :return:
        """

        super().__init__(nombre=nombre, fuente=fuente)

        # La receta del organismo es dónde se guarda toda la información necesaria para recrearlo de cero.
        # Contiene su nombre, un diccionario de los diccionarios de sus etapas, y la configuración actual del
        # organismo (ecuaciones activas y presas actuales para cada etapa.)

        símismo.receta = dict(nombre=nombre,
                              etapas={},
                              coefs={},
                              config={'ecuaciones': None,
                                      'presas': None
                                      }
                              )

        # Una lista de las etapas para facilitar el uso del organismo
        símismo.etapas = []

        # Actualizar el organismo
        símismo.actualizar()

    def actualizar(símismo):
        """
        Esta función simplemente se asegura de que todo en el organismo esté actualizado según la configuración
          actual en la receta. Si hay cualquier atributo del organismo que depiende de valore(s) en la receta,
          aquí es el lugar par actualizarlos.
        Esta función se llama automáticamente después de funciones tales como "secome()" y "quitar_etapa()".

        :return: Nada
        """

        # Actualizar el nombre del organismo
        símismo.nombre = símismo.receta['nombre']

        # Actualizar la lista de etapas según el orden cronológico de dichas etapas.
        símismo.etapas = sorted([x for x in símismo.receta['etapas']], key=lambda d: d['posición'])

    def añadir_etapa(símismo, nombre, posición, ecuaciones, paralela=False):
        """
        Esta función añade una etapa al organismo.

        :param nombre: El nombre de la etapa. Por ejemplo, "huevo", "juvenil_1", "pupa", "adulto"
        :type nombre: str

        :param posición: La posición cronológica de la etapa. Por ejemplo, "huevo" tendría posición 1, etc.
        :type posición: int

        :param ecuaciones: Un diccionario con los tipos de ecuaciones para esta etapa. (Siempre se puede cambiar
          más tarde con la función usar_ecuación()). Notar que las nuevas etapas tendrán TODAS las ecuaciones posibles
          en su diccionario inicial; la especificación de ecuación aquí únicamente determina cual(es) de estas se usarán
          para la calibración, simulación, etc.
          Tiene el formato: {Categoría_1: {subcategoría_1: tipo_de_ecuacion, ...}, Categoría_2: {...}, ...}
        :type ecuaciones: dict

        :param paralela: Indica si esta etapa se añnade de manera paralela a las otras etapas o de manera consecutiva.
        :type paralela: bool

        """

        # Crear el diccionario inicial para la etapa
        dic_etapa = dict(nombre=nombre,
                         posición=posición,
                         )

        # Guardar el diccionario en la receta del organismo
        símismo.receta['etapas'][nombre] = dic_etapa

        # Guardar las ecuaciones del organismo en la sección 'Coefs'] de la receta
        símismo.receta['coefs'][nombre] = Ec.gen_ec_inic(Ec.ecuaciones)

        # Copiar la selección de ecuaciones para la etapa a la configuración activa del organismo
        config_etp = símismo.receta['config']['ecuaciones'][nombre] = {}
        for categ, dic_categ in ecuaciones.items():
            config_etp[categ] = {}
            for subcateg, opción in dic_categ.items():
                config_etp[categ][subcateg] = opción

        # Crear una lista vaciá para eventualmente guardar las presas (si hay) de la nueva etapa
        símismo.receta['config']['presas'][nombre] = []

        # Aumentar la posición de las etapas que siguen la que añadiste
        if not paralela:
            for etp, dic_etp in símismo.receta['etapas'].items():
                if dic_etp['posición'] >= posición:
                    dic_etp['posición'] += 1

        # Actualizar el organismo
        símismo.actualizar()

    def quitar_etapa(símismo, nombre):
        # Quitar el diccionario de la etapa
        """
        Esta función quita una etapa del organismo.
        :param nombre: El nombre de la etapa a quitar (p. ej., "huevo" o "adulto")
        :type nombre: str
        """

        # Guardar la posición de la etapa a quitar
        posición = símismo.receta['etapas'][nombre]['posición']

        # Quitar el diccionario de la etapa de la receta del organismo
        símismo.receta['etapas'].pop(nombre)

        # Quitar las ecuaciones de la etapa de la lista de ecuaciones de la configuración actual del organismo
        símismo.receta['config']['ecuaciones'].pop(nombre)

        # Quitar la lista de presas de esta etapa de la configuración actual del organismo
        símismo.receta['config']['presas'].pop(nombre)

        # Disminuir la posición de las etapas que siguen la que acabas de quitar
        if posición not in [x['posición'] for x in símismo.receta['etapas'].values()]:
            # Sólo hacer el cambio si la etapa a quitar no era una etapa paralela
            for dic_etp in símismo.receta['etapas'].values():
                if dic_etp['posición'] >= posición:
                    dic_etp['posición'] -= 1

        # Actualizar el organismo
        símismo.actualizar()

    def aplicar_ecuación(símismo, etapa, tipo_ec):
        """
        Esta función aplica una configuración de ecuaciones a una etapa específica del organismo. No borar otras
          ecuaciones, sino simplemente cambia la ecuación activa usada para calibraciones, simulaciones, etc.

        :param etapa: El nombre de la etapa a cual esta ecuación se aplicará
        :type etapa: str

        :param tipo_ec: Un diccionario del tipo de ecuación que se aplicará. Debe tener el formato
          {categoría: {sub_categoría: opción_ecuación, sub_categoría: opción_ecuación, ...}, categoría: ...}
        :type tipo_ec: dict
        """

        for categ, dic_categ in tipo_ec.items():
            for sub_categ, opción_ec in dic_categ.items():
                símismo.receta['config']['ecuaciones'][etapa][categ][sub_categ] = opción_ec

    def secome(símismo, presa, etps_depred=None, etps_presa=None):
        """
        Esta función establece relaciones de depredador y presa entre organismos.

        :param presa: La presa (usar un objeto Organismo, no el nombre de la presa).
        :type presa: Organismo

        :param etps_depred: Lista de los nombres (cadena de carácteres) de las fases del depredador (este organismo)
          que se comen a la presa. Si se deja como "None", tomará todas las fases.
        :type etps_depred: list

        :param etps_presa: Lista de los nombres (cadena de carácteres) de las fases de la presa que se come el
          depredador (este organismo). Si se deja como "None", tomará todas las fases.
        :type etps_presa: list

        """

        # Si no se especificaron estapas específicas, tomar todas las etapas de los organismos.
        if etps_depred is None:
            etps_depred = [x for x in símismo.receta['etapas']]
        if etps_presa is None:
            etps_presa = [x for x in presa.receta['etapas']]

        # Si se le olvidó al utilisador poner sus etapas en forma de lista, hacerlo aquí
        if type(etps_presa) is str:
            etps_presa = [etps_presa]
        if type(etps_depred) is str:
            etps_depred = [etps_depred]

        # Guardar la relación de deprededor y presa en la configuración del organismo
        for e_depred in etps_depred:
            símismo.receta['config']['presas'][e_depred] = etps_presa

        # Reactualizar el organismo (necesario para asegurarse que las ecuaciones de depredador y prese tienen
        # todos los coeficientes necesarios para la nueva presa
        símismo.actualizar()

    def nosecome(símismo, presa, etps_depred=None, etps_presa=None):
        """
        Esta función borra relaciones de depredador y presa entre organismos.

        :param presa: La presa que ya no se come (usar un objeto Organismo, no el nombre de la presa).
        :type presa: Organismo

        :param etps_depred: Lista de los nombres (cadena de carácteres) de las fases del depredador (este organismo)
          que ya no se comen a la presa. Si se deja como "None", tomará todas las fases.
        :type etps_depred: list

        :param etps_presa: Lista de los nombres (cadena de carácteres) de las fases de la presa que ya no se come el
          depredador (este organismo). Si se deja como "None", tomará todas las fases.
        :type etps_presa: list

        """

        # Si no se especificaron estapas específicas, tomar todas las etapas de los organismos.
        if etps_depred is None:
            etps_depred = [x for x in símismo.receta['etapas']]
        if etps_presa is None:
            etps_presa = [x for x in presa.receta['etapas']]

        # Si se le olvidó al utilisador poner sus etapas en forma de lista, hacerlo aquí
        if type(etps_presa) is str:
            etps_presa = [etps_presa]
        if type(etps_depred) is str:
            etps_depred = [etps_depred]

        # Quitar la relación de deprededor y presa en la configuración del organismo
        for e_depred in etps_depred:  # Para cada etapa especificada del depredador...
            # Quitar cada etapa especificada de la presa
            for e_presa in etps_presa:
                símismo.receta['config']['presas'][e_depred].pop(e_presa)

            # Si ya no quedan estapas del organismo como presas, quitar su nombre del diccionario de presas
            if len(símismo.receta['config']['presas'][e_depred]) == 0:
                símismo.receta['config']['presas'].pop(e_depred)

        # No se reactualiza el organismo; los parámetros de interacciones con la antigua presa se quedan la receta
        # del organismo para uso futuro potencial.
