import INCERT.Ecuaciones as Ec
from NuevoCoso import Coso


class Organismo(Coso):
    """
    Esta clase representa cualquier organismo vivo en una red agroecológica.: insectos, agentes de
       enfermedad, etc. Maneja las ecuaciones y bases de datos de distribuciones probabilísticas para sus parámetros.
    Esta clase se llama directamente muy rara vez, porque se llama más facilmente por el uso de una de sus subclases
      (Insecto, Enfermedad, etc.). Hablando de subclases, puedes crear más subclases o sub-sub clases si te da las
      ganas. Por ejemplo, hay subclases de "Insecto" para la mayoría de los ciclos de vida posibles para insectos
      (Metamórfosis Completa, Metamórfosis Incompleta, etc.) y hacia sub-subclases de estas, si quieres.
      Un ejemplo de algo que podrías añadir sería una sub-subclase de "Sencillo" para pulgones, o sub-clases de
      Enfermedades para distintos tipos de enfermedades (enfermedades de insectos, enfermedades de hojas, de raíces,
      etc.) (¡Marcela!) :)
    Una cosa importante: si quieres crear una nueva subclase, sub-subclase, sub-sub-subclase (no importa), y quieres
      que la clase tenga métodos (fundiones) propias DISTINTAS de los métodos yá implementados en Organismo aquí,
      (por ejemplo, un método de .parasita() para parasitoides), tendrás que especificar un tipo de extensión de
      archivo único para tu clase (p.ej., '.ins' para Insecto) para que el módulo de Redes pueda distinguir archivos
      guardados específicos a tu nueva clase.

    """

    # La extensión de base para organismos
    ext = '.org'

    def __init__(símismo, nombre=None, fuente=None):
        """


        :param nombre: El nombre del organismo
        :type nombre: str

        :param fuente: Un archivo de organismo guardada (opcional) para cargar.
        :type fuente: str

        :return:
        """

        # Iniciar el Organismo como Coso
        super().__init__(nombre=nombre, fuente=fuente)

        # Una lista ordenada de las etapas del organismo (para facilitar su acceso)
        símismo.etapas = []

        # Aquí se guardan cambios al estátus del organismo que NO se guardan con su receta (hay que definirlas cada
        # vez que se crea el objeto del organismo). Ejemplo: presas y huéspedes de cada etapa del organismo.
        símismo.config = {}

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
        símismo.etapas = sorted([x for x in símismo.receta['estr'].values()], key=lambda d: d['posición'])

    def añadir_etapa(símismo, nombre, posición, ecuaciones):
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

        """

        # Crear el diccionario inicial para la etapa
        dic_etapa = dict(posición=posición,
                         ecs=ecuaciones.copy()  # Compiar la selección de tipos de ecuaciones
                         )

        # Guardar el diccionario en la receta del organismo
        símismo.receta['estr'][nombre] = dic_etapa

        # Guardar las ecuaciones del organismo en la sección 'Coefs'] de la receta
        símismo.receta['coefs'][nombre] = Ec.gen_ec_inic(Ec.ecs_orgs)

        # Crear diccionarios para eventualmente contener las presas o huéspedes (si hay) de la nueva etapa
        símismo.config[nombre] = {'presas': {}, 'huéspedes': {}}

        # Aumentar la posición de las etapas que siguen la que añadiste
        for etp, dic_etp in símismo.receta['estr'].items():
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
        posición = símismo.receta['estr'][nombre]['posición']

        # Quitar el diccionario de la etapa de la receta del organismo
        símismo.receta['estr'].pop(nombre)

        # Quitar las ecuaciones de la etapa de la lista de ecuaciones del organismo
        símismo.receta['coefs']['ecuaciones'].pop(nombre)

        # Quitar la etapa de la configuración actual del organismo
        símismo.config.pop(nombre)

        # Disminuir la posición de las etapas que siguen la que acabas de quitar
        for dic_etp in símismo.receta['estr'].values():
            if dic_etp['posición'] > posición:
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
                símismo.receta['estr'][etapa]['ecuaciones'][categ][sub_categ] = opción_ec

    def victimiza(símismo, víctima, etps_símismo=None, etps_víctima=None, método='presa'):
        """
        Esta función establece relaciones de  entre organismos.

        :param víctima: La presa (usar un objeto Organismo, no el nombre de la presa).
        :type víctima: Organismo

        :param etps_símismo: Lista de los nombres (cadena de carácteres) de las fases del depredador (este organismo)
          que se comen a la presa. Si se deja como "None", tomará todas las fases.
        :type etps_símismo: list | str

        :param etps_víctima: Lista de los nombres (cadena de carácteres) de las fases de la presa que se come el
          depredador (este organismo). Si se deja como "None", tomará todas las fases.
        :type etps_víctima: list | str

        :param método:
        :type método:

        """

        # Verificar que el método es válido
        if método not in ['presa', 'huésped']:
            raise ValueError('Método de relación víctima no válido.')

        # Si no se especificaron etapas específicas, tomar todas las etapas de los organismos.

        if etps_símismo is None:
            etps_símismo = [x for x in símismo.receta['estr']]
        if etps_víctima is None:
            etps_víctima = [x for x in víctima.receta['estr']]

        # Si se te olvidó poner el nombre de tus etapasen forma de lista, el programa lo hará para ti

        if type(etps_víctima) is str:
            etps_víctima = [etps_víctima]
        if type(etps_símismo) is str:
            etps_símismo = [etps_símismo]

        # Guardar la relación de deprededor y presa en la configuración del organismo
        for e_depred in etps_símismo:
            dic_víc = símismo.receta['estr'][e_depred][método]

            # Si necesario, añadir el nombre de la presa al diccionario de víctimas
            if víctima.nombre not in dic_víc:
                dic_víc[víctima.nombre] = []

            for e_presa in etps_víctima:
                if e_presa not in dic_víc:  # Evitar de añadir una presa más que una vez por error
                    dic_víc[víctima.nombre].append(e_presa)

        # Reactualizar el organismo (necesario para asegurarse que las ecuaciones de depredador y prese tienen
        # todos los coeficientes necesarios para la nueva presa
        símismo.actualizar()

    def novictimiza(símismo, víctima, etps_símismo=None, etps_víctima=None, método='presa'):
        """
        Esta función borra relaciones de depredador y presa entre organismos.

        :param víctima: La presa que ya no se come (usar un objeto Organismo, no el nombre de la presa).
        :type víctima: Organismo

        :param etps_símismo: Lista de los nombres (cadena de carácteres) de las fases del depredador (este organismo)
          que ya no se comen a la presa. Si se deja como "None", tomará todas las fases.
        :type etps_símismo: list | str

        :param etps_víctima: Lista de los nombres (cadena de carácteres) de las fases de la presa que ya no se come el
          depredador (este organismo). Si se deja como "None", tomará todas las fases.
        :type etps_víctima: list | str

        :param método:
        :type método:

        """

        # Verificar que el método es válido
        if método not in ['presa', 'huésped']:
            raise ValueError('Método de relación víctima no válido.')

        # Si no se especificaron etapas específicas, tomar todas las etapas de los organismos.

        if etps_símismo is None:
            etps_símismo = [x for x in símismo.receta['estr']]
        if etps_víctima is None:
            etps_víctima = [x for x in víctima.receta['estr']]

        # Si se te olvidó poner el nombre de tus etapasen forma de lista, el programa lo hará para ti

        if type(etps_víctima) is str:
            etps_víctima = [etps_víctima]
        if type(etps_símismo) is str:
            etps_símismo = [etps_símismo]

        # Quitar la relación de deprededor y presa en la configuración del organismo

        for e_depred in etps_símismo:  # Para cada etapa especificada del depredador...

            dic_víc = símismo.receta['estr'][e_depred][método]

            # Quitar cada etapa especificada de la presa
            for e_presa in etps_víctima:

                # Vamos a ignorar etapas que no eran en la lista de víctimas para empezar (posible por error del
                # usuario o por uso de 'etps_víctima = None' para referenciar todas las etapas de la víctima.
                try:
                    dic_víc[víctima.nombre].pop(e_presa)
                except KeyError:
                    pass

            # Si ya no quedan estapas del organismo como presas, quitar su nombre del diccionario de presas
            if len(dic_víc[víctima.nombre]) == 0:
                dic_víc.pop(víctima.nombre)

        # No se reactualiza el organismo.

        # Los parámetros de interacciones con la antigua presa se quedan la receta del organismo para uso futuro
        # potencial.

    def _sacar_coefs_interno(símismo):
        lista_coefs = []

        for etp in símismo.etapas:
            for categ in sorted(Ec.ecs_orgs):
                for sub_categ in sorted(Ec.ecs_orgs[categ]):
                    nombre_ec = símismo.receta['estr'][etp]['ecuaciones'][categ][sub_categ]
                    dic_parám = símismo.receta['coefs'][etp][categ][sub_categ][nombre_ec]
                    lista_coefs.append(dic_parám)

        return lista_coefs

    def _sacar_líms_coefs_interno(símismo):
        lista_líms = []

        for etp in símismo.etapas:
            for categ in sorted(Ec.ecs_orgs):
                for sub_categ in sorted(Ec.ecs_orgs[categ]):
                    dic_paráms = símismo.receta['estr'][etp]['ecuaciones'][categ][sub_categ]
                    for parám in sorted(dic_paráms):
                        líms = Ec.ecs_orgs[categ][sub_categ][parám]['límites']
                        lista_líms.append(líms)

        return lista_líms
