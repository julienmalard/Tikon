from tikon.Coso import Coso


# Esta clase representa los suelos de una parcela.
class Suelo(Coso):

    ext = '.suel'

    def __init__(símismo, nombre, directorio):
        # El diccionario de los datos para cada suelo
        dic = dict(Nombre=nombre, Textura_suelo="", Profundidad_suelo=(), Color="", Albedo=(), Límite_evap=(),
                   Drenaje=(), Factor_mineral=(), Factor_fotosyn=(), Método_pH="", Metodo_potasio="",
                   Profund_muestras=[], Fósforo_extract=[], Fósforo_total=[], Fósforo_orgán=[], CaCO3=[],
                   Aluminio=[], Hierro=[], Manganesio=[], Satur_base=[], Isoterm_P_a=[], Isoterm_P_b=[],
                   Potas_intercamb=[], Magnesio=[], Sodio=[], Solfor=[], Conduct_eléc=[],
                   Calcio_intercamb=[], Límite_bajo=[], Límite_alto=[], Límite_alto_sat=[],
                   Factor_crec_raíz=[], Cond_hidró_sat=[], Densidad_suelo=[], Carbono_orgán=[],
                   Fracción_argi=[], Fracción_lim=[], Fracción_rocas=[], Nitró_total=[], pH_agua=[],
                   pH_tamp=[], Poten_intercamb_cat=[])
        # Esta variable se initializa como Coso
        super().__init__(nombre=nombre, dic=dic, directorio=directorio)
