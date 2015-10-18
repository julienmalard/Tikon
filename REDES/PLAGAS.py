from COSO import Coso


# Esta clase representa una red agroecológica
class Red(Coso):
    def __init__(self, *args, **kwargs):
        # El diccionario de los datos para cada red
        self.dic_base = dict(Insectos=[], tipo_ecuaciones="")
        self.ext = "red"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        super().__init__(*args, **kwargs)  # Esta clase se initializa como describido en Coso
        self.insectos = {}
        self.tipo_ecuaciones = ""
        self.poblaciones = {}

    def ejec(self, tipo_ecuaciones, poblaciones_iniciales):
        self.tipo_ecuaciones = tipo_ecuaciones
        for insecto in self.dic["Insectos"]:  # Migrar los insectos del diccionario al objeto si mismo
            self.insectos[self.dic["Insectos"][insecto].nombre] = self.dic["Insectos"][insecto]
        for insecto in self.insectos:  # Crear las instancias de los insectos
            self.insectos[insecto].ejec(otros_insectos=self.dic["Insectos"])
            # Para guardar los datos de poblaciones (para pruebas del modelo)
            self.poblaciones[insecto] = {}
            for fase in self.insectos[insecto].fases:
                self.poblaciones[insecto][fase] = []
        for insecto in poblaciones_iniciales:  # Inicializar las poblaciones
            if insecto in self.insectos:
                for fase in poblaciones_iniciales[insecto]:
                    self.insectos[insecto].fases[fase].pob = poblaciones_iniciales[insecto][fase]

    def incr(self, paso, estado_cultivo):
        poblaciones = {}  # Para comunicación con el submódulo PARCELA
        for insecto in self.insectos:
            self.insectos[insecto].incr(paso, self.tipo_ecuaciones, estado_cultivo)
            poblaciones[insecto] = self.insectos[insecto].pob  # Para comunicación con el submódulo PARCELA
            for fase in self.insectos[insecto].pob:
                if fase in self.poblaciones[insecto].keys():
                    self.poblaciones[insecto][fase].append(self.insectos[insecto].pob[fase])
        return poblaciones


class Insecto(Coso):
    def __init__(self, *args, **kwargs):
        # El diccionario de los datos para cada insecto
        self.dic_base = dict(ciclo_vida="")
        self.ext = "int"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        super().__init__(*args, **kwargs)  # Esta clase se initializa como describido en Coso
        # Crear instancias de etapas de desarrollo según el ciclo de vida del insecto
        self.fases = {}
        if self.dic["ciclo_vida"] == "simple":
            self.fases = dict(Adulto=Fase(self.nombre + "_adulto"))
            self.fases["Adulto"].dic["fuente"] = self.fases["Adulto"]
        elif self.dic["ciclo_vida"] == "dos_fases":
            self.fases = dict(Juvenil=Fase(self.nombre + "_juvenil"), Adulto=Fase(self.nombre + "_adulto"))
            self.fases["Juvenil"].dic["fuente"] = self.fases["Adulto"]
            self.fases["Adulto"].dic["fuente"] = self.fases["Juvenil"]
        elif self.dic["ciclo_vida"] == "cuatro_fases":
            self.fases = dict(Huevo=Fase(self.nombre + "_huevo"), Juvenil=Fase(self.nombre + "_juvenil"),
                              Pupa=Fase(self.nombre + "pupa"), Adulto=Fase(self.nombre + "_adulto"))
            self.fases["Huevo"].dic["fuente"] = self.fases["Adulto"]
            self.fases["Juvenil"].dic["fuente"] = self.fases["Huevo"]
            self.fases["Pupa"].dic["fuente"] = self.fases["Juvenil"]
            self.fases["Adulto"].dic["fuente"] = self.fases["Pupa"]

        # Para guardar los datos de poblaciones
        self.pob = dict(Adulto=(), Juvenil=(), Huevos=(), Larva=(), Pupa=())

    # Esta función inicializa el insecto basado en la red trófica utilizada
    def ejec(self, otros_insectos):
        for etapa in self.fases:
            self.fases[etapa].ejec(otros_insectos, self.dic["ciclo_vida"])

    # Esta función incrementa la población de un insecto (para cada etapa de desarrollo del insecto)
    def incr(self, paso, tipo_ecuaciones, estado_cultivo):
        for fase in self.fases:
            self.fases[fase].incr(paso, tipo_ecuaciones, estado_cultivo)
        self.pob["Adulto"] = self.fases["Adulto"].pob
        if self.dic["ciclo_vida"] == "dos_fases" or self.dic["ciclo_vida"] == "cuatro_fases":
            self.pob["Juvenil"] = self.fases["Juvenil"].pob
        if self.dic["ciclo_vida"] == "cuatro_fases":
            self.pob["Huevo"] = self.fases["Huevo"].pob
            self.pob["Pupa"] = self.fases["Pupa"].pob


class Fase(Coso):
    def __init__(self, *args, **kwargs):
        # El diccionario de los datos para cada insecto
        self.dic_base = dict(Depredadores=[], Presas=[], coefs={})
        self.ext = "etp"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        super().__init__(*args, **kwargs)  # Esta clase se initializa como describido en Coso

        self.ciclo_vida = ""
        # Para poner las presas y deprededores en la red actual
        self.depredadores_act = []
        self.presas_act = []
        # La población de la etapa del insecto
        self.pob = ()

    # Esta función inicializa el insecto basado en la red trófica utilizada
    def ejec(self, otros_insectos, ciclo_vida):
        self.ciclo_vida = ciclo_vida
        # Utilizar sólamente los depredadoes y las presas en la red trófica utilizada
        for depredador in self.dic["Depredadores"]:
            if depredador.nombre.split('_')[0] in otros_insectos:
                self.depredadores_act.append(depredador)
        for presa in self.dic["Presas"]:
            # Si la presa es un otro insecto y existe en la red agroecológica especificada
            if type(presa) is Fase and presa.nombre.split('_')[0] in otros_insectos:
                self.presas_act.append(presa)
            elif type(presa) is str:  # Si la "presa" es un cultivo
                self.presas_act.append(presa)
        for depredador in self.depredadores_act:
            self.dic["coefs"][depredador.nombre] = ()
        for presa in self.presas_act:
            if type(presa) is Fase:  # Si la presa es otro insecto...
                self.dic["coefs"][presa.nombre] = ()
            elif type(presa) is str:  # Si la "presa" es una planta...
                self.dic["coefs"][presa] = ()

    def incr(self, paso, tipo_ecuaciones, estado_cultivo):
        # Para ecuaciones Lotka-Volterra
        if tipo_ecuaciones == "Lotka-Voltera":
            if self.ciclo_vida is not "simple":
                return "Error: Tipo de ecuación Lotka-Voltera para insecto " + self.nombre + \
                       " no está disponible para insectos con ciclos de vida complejos."
            else:
                r = 0
                if type(self.presas_act[0]) is Fase:  # si el insecto es un depredador
                    for presa in self.presas_act:
                        r += presa.población * self.dic["coefs"][presa.nombre]  # Consumo de presas
                elif type(self.presas_act[0]) is str:  # Si el insecto es un herbívoro
                    r = self.dic["coefs"]["r"]
                self.pob *= r

                for depredador in self.depredadores_act:
                    self.pob -= depredador.población * self.dic["coefs"][depredador.nombre]
                if self.pob < 0:
                    self.pob = 0

        # Un tipo de ecuación donde las presas determinan el crecimiento poblacional por la mortalidad del depredador
        elif tipo_ecuaciones == "presas_mortalidad":
            # Crecimiento poblacional (por ejemplo, larvas aumentan por la eclosión de huevos). Notar que, aparte
            # del caso de un ciclo de vida simple, la fuente del crecimiento está externa a la fase actual y
            # "taza_crec" se refiere a la taza de conversión de la fase presente a la próxima fase.

            # La taza de conversión actual de esta fase del insecto depiende de la fase anterior
            taza_conv = self.dic["fuente"]["coefs"]["r"]

            # La población se aumenta por la población de la fase anterior por la taza de conversión...
            self.pob += max(self.dic["fuente"].pob * taza_conv * paso, self.dic["fuente"].pob)
            # ...y disminuir la población de la fase anterior (al menos que era un adulto, porque adultos ponen huevos,
            # no se convierten en huevos).
            if "adulto" not in self.dic["fuente"].nombre.lower():
                self.dic["fuente"].pob -= max(self.dic["fuente"].pob * taza_conv * paso, self.dic["fuente"].pob)

            # Quitar los individuales que fueron comidos
            for depredador in self.depredadores_act:
                predación = self.dic["coefs"][depredador.nombre]
                self.pob -= depredador.población * predación * paso
            # Quitar los individuales que se mueren de otras causas (incluso falta de comida):
            mortalidad = self.dic["coefs"]["mortalidad"]
            for presa in self.presas_act:
                mortalidad += presa.población * self.dic["coefs"][presa.nombre]  # Consumo de presas
            self.pob -= self.pob * mortalidad * paso

            if self.pob < 0:
                self.pob = 0

        elif tipo_ecuaciones == "capacidad_de_carga":
            if self.ciclo_vida is not "simple":
                return 'Error: Tipo de ecuación "Capacidad de Carga" para insecto " + self.nombre + ' \
                       'no está disponible para insectos con ciclos de vida complejos.'
            else:
                r = self.dic["coefs"]["r"]
                K = 0.001  # K tiene que ser mayor que 0 para evitar dividir por 0 en la ecuación dN/dt = rN(K-N)/K
                for presa in self.presas_act:
                    if type(self.presas_act[0]) is Fase:  # si el insecto es un depredador
                        K += presa.pob * self.dic["coefs"][presa.nombre]  # Consumo de presas
                    elif type(self.presas_act[0]) is str:  # Si el insecto es un herbívoro
                        K = self.dic["coefs"][presa] * estado_cultivo[presa]
                self.pob += r * self.pob * (K - self.pob)/K * paso
                for depredador in self.depredadores_act:
                    predación = self.dic["coefs"][depredador.nombre]
                    self.pob -= depredador.pob * predación * paso

                if self.pob < 0:
                    self.pob = 0
