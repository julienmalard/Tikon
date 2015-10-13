from COSO import Coso
from CULTIVO.CULTIVO import Cultivo
from CULTIVO.SUELO import Suelo
from PLAGAS.REDES import Red
from CULTIVO.VARIEDAD import Variedad
import os


# Una parcela se refiere a una unidad de tierra homógena en sus suelo, cultivo(s)
# y otras propiedades
class Parcela(Coso):
    def __init__(simismo, suelos_común, variedades_común, redes_común, *args, **kwargs):
        simismo.dic_base = {"Suelo": "", "Variedad": "", "Meteo": "", "RedAE": "", "Long": (), "Lat": (),
                            "Área": (), "Surcos": (), "Long_surcos": (), 'Pendiente_orientación': '', 'Piedras': '',
                            'Fecha_init': '',
                            'Manejo': dict(fecha_siembra="", Fecha_emergencia=[], Población_siembra=[],
                                           Población_emerg=[], Método_siembra=[], Distribución_siembra=[],
                                           Espacio_surcos=[], Dirrección_surcos=[], Profund_siembra=[],
                                           Peso_material_sembrado=[], Edad_transplantaciones=[],
                                           Temp_transplantación=[], Plantas_por_montículo=[], Eficiencia_irrig=[],
                                           Profund_manejo_irrig=[], Hum_empiezo_irrig_auto=[], Hum_fin_irrig_auto=[],
                                           Estadio_crec_fin_irrig=[], Método_irrig=[], Cantidad_por_irrig=[],
                                           Fecha_abono=[], Material_abono=[], Método_app_abono=[], Profund_abono=[],
                                           Abono_N=[], Abono_P=[], Abono_K=[], Abono_Ca=[], Abono_otro_conc=[],
                                           Abono_otro_cód=[], Fecha_incorp_resid=[], Material_resid=[], Resid_N=[],
                                           Resid_P=[], Resid_K=[], Resid_porcent_incorp=[], Resid_prodund_incorp=[],
                                           Fecha_labranza=[], Herramienta_labranza=[], Profund_labranza=[],
                                           Fecha_cosecha=[], Estadio_cosecha=[], Componente_cosecha=[],
                                           Grupo_tamaño_cosecha=[], Porcent_cosecha=[], Irrig=True, Irrig_auto=True,
                                           Cant_irrig_auto=(),
                                           )
                            }
        simismo.suelos_común = suelos_común
        simismo.variedades_común = variedades_común
        simismo.redes_común = redes_común
        super().__init__(*args, **kwargs)
        simismo.ext = "par"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        # Crear la carpeta para la parcela:
        if (not simismo.variedades_común) or (not simismo.suelos_común):
            if not os.path.exists(os.path.splitext(simismo.documento)[0]):  # splitext quita la extensión
                os.makedirs(os.path.splitext(simismo.documento)[0])

        # Dar el directorio apropiado a la variedad de cultivo y el suelo utilizados para esta parcela
        if simismo.variedades_común:  # Si la parcela comparte variedades con otros proyectos (para calibración)
            carpeta_variedad = "Parcelas" + "\\" + "Variedades"
        else:  # Si la parcela tiene sus variedades individuales (para calibración)
            carpeta_variedad = simismo.carpeta
        if simismo.suelos_común:  # Si la parcela comparte suelo con otros proyectos (para calibración)
            carpeta_suelo = "Parcelas" + "\\" + "Suelos"
        else:  # Si la parcela tiene sus suelos individuales (para calibración)
            carpeta_suelo = simismo.carpeta
        if simismo.redes_común:
            carpeta_redes = "Parcelas" + "\\" + "Redes"
        else:  # Si la parcela tiene sus suelos individuales (para calibración)
            carpeta_redes = simismo.carpeta

        # Definir el cultivo y la red agroecológica
        simismo.red = Red(nombre=simismo.dic["RedAE"], carpeta=carpeta_redes, reinit=simismo.reinit)
        simismo.variedad = Variedad(nombre=simismo.dic["Variedad"], carpeta=carpeta_variedad,
                                    reinit=simismo.reinit)
        simismo.suelo = Suelo(nombre=simismo.dic["Variedad"], carpeta=carpeta_suelo, reinit=simismo.reinit)
        simismo.cultivo = Cultivo(nombre=simismo.nombre + "_" + simismo.dic["Cultivo"], cultivo=simismo.cultivo,
                                  variedad=simismo.variedad, suelo=simismo.dic["Suelo"],
                                  meteo=simismo.dic["Meteo"], manejo=simismo.dic["Manejo"]
                                  )

        # Poner a 0 los valores iniciales del cultivo y de los insectos
        simismo.estado_cultivo = {}
        for var in simismo.cultivo.egresos:
            simismo.estado_cultivo[var] = ()
        simismo.daño_plagas = {}
        simismo.insectos = {}
        for insecto in simismo.red.insectos:
            simismo.insectos[insecto] = ()

        # Para guardar los resultados de la simulación
        simismo.resultados = dict(Emigración=[], Imigración=[], Día=[0])
        for dato in simismo.cultivo.egresos:
            simismo.resultados[dato] = ()
        for insecto in simismo.insectos:
            simismo.resultados[insecto]["Emigración"] = [0]
            simismo.resultados[insecto]["Imigración"] = [0]

        # Esta función inicializa los modelos para la parcela

    def ejec(simismo, fecha_init):
        # Una carpeta para guardar los resultados del modelo de cultivos
        carpeta_egr = os.path.join(simismo.carpeta, "documentos_mod_cul")
        # El modelo del cultivo define el tiempo para la simulación:
        simismo.cultivo.ejec(fecha_init, carpeta=carpeta_egr)
        # El modelo de plagas sigue mientras hay un modelo de cultivo activo
        simismo.red = eval(simismo.dic["RedAE"])
        simismo.resultados["Día"] = [0]

    def incr(simismo, paso):
        if simismo.cultivo.proceso.poll is None:
            # Incrementar los cultivos y la red
            simismo.cultivo.incr(paso, simismo.daño_plagas)
            simismo.estado_cultivo = simismo.cultivo.egresos
            simismo.daño_plagas, simismo.insectos = simismo.red.incr(simismo.estado_cultivo, paso)
            # Guardar datos
            for dato in simismo.estado_cultivo:
                if dato not in simismo.resultados:
                    simismo.resultados[dato] = []
                simismo.resultados[dato].append(simismo.estado_cultivo[dato])
            for dato in simismo.daño_plagas:
                if dato not in simismo.resultados:
                    simismo.resultados[dato] = []
                simismo.resultados[dato].append(simismo.daño_plagas[dato])
            for dato in simismo.insectos:
                if dato not in simismo.resultados:
                    simismo.resultados[dato] = []
                simismo.resultados[dato].append(simismo.insectos[dato])
            # Incrementar el tiempo
            simismo.resultados["Día"].append = simismo.resultados["Día"][-1] + paso
        else:
            return "Modelo de cultivo terminado."
