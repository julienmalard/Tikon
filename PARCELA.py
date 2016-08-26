import os

from CULTIVO.CULTIVO import Cultivo


# Una parcela se refiere a una unidad de tierra homógena en sus suelo, cultivo(s)
# y otras propiedades
class Parcela(object):
    def __init__(símismo, nombre, directorio, suelos_común, variedades_común, redes_común):
        símismo.dic = {"Suelo": "", "Variedad": "", "Meteo": "", "RedAE": "", "Long": (), "Lat": (),
                       "Área": (), "Surcos": (), "Long_surcos": (), 'Pendiente_orientación': '', 'Piedras': '',
                       'Fecha_init': '',
                       'Manejo': dict(Fecha_siembra="", Fecha_emergencia="", Población_siembra=[],
                                      Población_emerg=[], Método_siembra=[], Distribución_siembra=[],
                                      Espacio_surcos=[], Dirección_surcos=[], Profund_siembra=[],
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
                                      Cant_irrig_auto=()
                                      )
                       }
        símismo.suelos_común = suelos_común
        símismo.variedades_común = variedades_común
        símismo.redes_común = redes_común
        símismo.suelo = None
        símismo.variedad = None
        símismo.meteo = None
        símismo.red = None

        # Crear la carpeta para la parcela:
        if (not símismo.variedades_común) or (not símismo.suelos_común):
            if not os.path.exists(os.path.splitext(símismo.documento)[0]):  # splitext quita la extensión
                os.makedirs(os.path.splitext(símismo.documento)[0])

        # Dar el directorio apropiado a la variedad de cultivo y el suelo utilizados para esta parcela
        if símismo.variedades_común:  # Si la parcela comparte variedades con otros proyectos (para calibración)
            carpeta_variedad = "Parcelas" + "\\" + "Variedades"
        else:  # Si la parcela tiene sus variedades individuales (para calibración)
            carpeta_variedad = símismo.carpeta
        if símismo.suelos_común:  # Si la parcela comparte suelo con otros proyectos (para calibración)
            carpeta_suelo = "Parcelas" + "\\" + "Suelos"
        else:  # Si la parcela tiene sus suelos individuales (para calibración)
            carpeta_suelo = símismo.carpeta
        if símismo.redes_común:
            carpeta_redes = "Parcelas" + "\\" + "Redes"
        else:  # Si la parcela tiene sus suelos individuales (para calibración)
            carpeta_redes = símismo.carpeta

        # Definir el cultivo y la red agroecológica
        símismo.cultivo = Cultivo(cultivo=símismo.cultivo,
                                  variedad=símismo.variedad, suelo=símismo.dic["Suelo"],
                                  meteo=símismo.dic["Meteo"], manejo=símismo.dic
                                  )

        # Poner a 0 los valores iniciales del cultivo y de los insectos
        símismo.estado_cultivo = {}
        for var in símismo.cultivo.egresos:
            símismo.estado_cultivo[var] = ()
        símismo.daño_plagas = {}
        símismo.insectos = {}
        for insecto in símismo.red.insectos:
            símismo.insectos[insecto] = ()

        # Para guardar los resultados de la simulación
        símismo.resultados = dict(Emigración=[], Imigración=[], Día=[0])
        for dato in símismo.cultivo.egresos:
            símismo.resultados[dato] = ()
        for insecto in símismo.insectos:
            símismo.resultados[insecto]["Emigración"] = [0]
            símismo.resultados[insecto]["Imigración"] = [0]

        # Esta función inicializa los modelos para la parcela

    def ejec(símismo):
        # Una carpeta para guardar los resultados del modelo de cultivos
        carpeta_egr = os.path.join(símismo.carpeta, "documentos_mod_cul")
        # El modelo del cultivo define el tiempo para la simulación:
        símismo.cultivo.ejec(carpeta=carpeta_egr)
        # El modelo de plagas sigue mientras hay un modelo de cultivo activo
        símismo.red = eval(símismo.dic["RedAE"])
        símismo.resultados["Día"] = [0]

    def incr(símismo, paso):
        if símismo.cultivo.proceso.poll is None:
            # Incrementar los cultivos y la red
            símismo.cultivo.incr(paso, símismo.daño_plagas)
            símismo.estado_cultivo = símismo.cultivo.egresos
            símismo.daño_plagas, símismo.insectos = símismo.red.incr(símismo.estado_cultivo, paso)
            # Guardar datos
            for dato in símismo.estado_cultivo:
                if dato not in símismo.resultados:
                    símismo.resultados[dato] = []
                símismo.resultados[dato].append(símismo.estado_cultivo[dato])
            for dato in símismo.daño_plagas:
                if dato not in símismo.resultados:
                    símismo.resultados[dato] = []
                símismo.resultados[dato].append(símismo.daño_plagas[dato])
            for dato in símismo.insectos:
                if dato not in símismo.resultados:
                    símismo.resultados[dato] = []
                símismo.resultados[dato].append(símismo.insectos[dato])
            # Incrementar el tiempo
            símismo.resultados["Día"].append = símismo.resultados["Día"][-1] + paso
        else:
            return "Modelo de cultivo terminado."
