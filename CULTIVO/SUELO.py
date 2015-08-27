from COSO import Coso


# Esta clase representa los suelos de una parcela.
class Suelo(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada suelo
        simismo.dic_base = dict(Textura_suelo="", Profundidad_suelo=(), Color="", Albedo=(), Límite_evap=(), Drenaje=(),
                             Factor_mineral=(), Factor_fotosyn=(), Método_pH="", Metodo_potasio="", Profund_muestras=[],
                             Fósforo_extract=[], Fósforo_total=[], Fósforo_orgán=[], CaCO3=[], Aluminio=[], Hierro=[],
                             Manganesio=[], Satur_base=[], Isoterm_P_a=[], Isoterm_P_b=[], Potas_intercamb=[],
                             Magnesio=[], Sodio=[], Solfor=[], Conduct_eléc=[], Calcio_intercamb=[], Límite_bajo=[],
                             Límite_alto=[], Límite_alto_sat=[], Factor_crec_raíz=[], Cond_hidró_sat=[],
                             Densidad_suelo=[], Carbono_orgán=[], Fracción_argi=[], Fracción_lim=[], Fracción_rocas=[],
                             Nitró_total=[], pH_agua=[], pH_tamp=[], Poten_intercamb_cat=[])
        super().__init__(*args, **kwargs)  # Esta variable se initializa como
        simismo.ext = "su"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)

# Pruebas:
prueba = Suelo("suelo", {'Conductividad': [0.2, 0.3, 0.4]})
print(prueba.escribir("C:\DSSAT45\Soil"))
print(prueba.dic)
prueba.dic = {}
prueba.leer("C:\DSSAT45\Soil")
print(prueba.dic)
