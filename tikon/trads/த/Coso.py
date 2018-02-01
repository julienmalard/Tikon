from tikon.Coso import Coso
from tikon.Coso import Simulable


class Coso(Coso):

    def actualizar(தன்):
        return super().actualizar()

    def especificar_apriori(தன்):
        return super().especificar_apriori()

    def borrar_calib(தன், id_calib, recursivo=True):
        return super().borrar_calib(id_calib=id_calib, recursivo=recursivo)

    def limpiar_especificados(தன், recursivo=True):
        return super().limpiar_especificados(recursivo=recursivo)

    def guardar_especificados(தன், nombre_dist="dist_especificada"):
        return super().guardar_especificados(nombre_dist=nombre_dist)

    def guardar(தன், திட்டம்=None, especificados=False, iterativo=True):
        return super().guardar(proyecto=திட்டம், especificados=especificados, iterativo=iterativo)

    def cargar(தன், fuente):
        return super().cargar(fuente=fuente)

    def ver_coefs_no_espec(தன்):
        return super().ver_coefs_no_espec()

    def generar_aprioris(cls, directorio=None):
        return super().generar_aprioris(directorio=directorio)


class Simulable(Simulable):

    def actualizar(தன்):
        return super().actualizar()

    def incrementar(தன், paso, i, detalles, extrn):
        return super().incrementar(paso=paso, i=i, detalles=detalles, extrn=extrn)

    def simular(தன், exper=None, பெயர்=None, paso=1, tiempo_final=None, n_rep_parám=100, n_rep_estoc=100,
                calibs="Todos", usar_especificadas=False, detalles=True, dibujar=True, directorio_dib=None,
                mostrar=True, opciones_dib=None, dib_dists=True, valid=False, depurar=False):
        return super().simular(exper=exper, nombre=பெயர், paso=paso, tiempo_final=tiempo_final, n_rep_parám=n_rep_parám,
                               n_rep_estoc=n_rep_estoc, calibs=calibs, usar_especificadas=usar_especificadas,
                               detalles=detalles, dibujar=dibujar, directorio_dib=directorio_dib, mostrar=mostrar,
                               opciones_dib=opciones_dib, dib_dists=dib_dists, valid=valid, depurar=depurar)

    def calibrar(தன், பெயர்=None, aprioris=None, exper=None, paso=1, n_rep_estoc=10, tiempo_final=None, n_iter=10000,
                 quema=100, extraer=10, método="Metrópolis adaptivo", pedazitos=None, usar_especificadas=True,
                 dibujar=False, depurar=False):
        return super().calibrar(nombre=பெயர், aprioris=aprioris, exper=exper, paso=paso, n_rep_estoc=n_rep_estoc,
                                tiempo_final=tiempo_final, n_iter=n_iter, quema=quema, extraer=extraer, método=método,
                                pedazitos=pedazitos, usar_especificadas=usar_especificadas, dibujar=dibujar,
                                depurar=depurar)

    def avanzar_calib(தன், rep=10000, quema=100, extraer=10):
        return super().avanzar_calib(rep=rep, quema=quema, extraer=extraer)

    def guardar_calib(தன், descrip, utilizador, contacto=""):
        return super().guardar_calib(descrip=descrip, utilizador=utilizador, contacto=contacto)

    def añadir_exp(தன், experimento, corresp):
        return super().añadir_exp(experimento=experimento, corresp=corresp)

    def validar(தன், exper, பெயர்=None, calibs=None, paso=1, n_rep_parám=20, n_rep_estoc=20, usar_especificadas=False,
                detalles=False, guardar=True, dibujar=True, mostrar=False, opciones_dib=None, dib_dists=True,
                depurar=False):
        return super().validar(exper=exper, nombre=பெயர், calibs=calibs, paso=paso, n_rep_parám=n_rep_parám,
                               n_rep_estoc=n_rep_estoc, usar_especificadas=usar_especificadas, detalles=detalles,
                               guardar=guardar, dibujar=dibujar, mostrar=mostrar, opciones_dib=opciones_dib,
                               dib_dists=dib_dists, depurar=depurar)

    def sensibilidad(தன், பெயர், exper, n, método="Sobol", calibs=None, por_dist_ingr=0.95, n_rep_estoc=30,
                     tiempo_final=None, detalles=False, usar_especificadas=True, opciones_sens=None, dibujar=False):
        return super().sensibilidad(nombre=பெயர், exper=exper, n=n, método=método, calibs=calibs,
                                    por_dist_ingr=por_dist_ingr, n_rep_estoc=n_rep_estoc, tiempo_final=tiempo_final,
                                    detalles=detalles, usar_especificadas=usar_especificadas,
                                    opciones_sens=opciones_sens, dibujar=dibujar)

    def dibujar(தன், mostrar=True, directorio=None, exper=None):
        return super().dibujar(mostrar=mostrar, directorio=directorio, exper=exper)

    def dibujar_calib(தன்):
        return super().dibujar_calib()

    def especificar_apriori(தன்):
        return super().especificar_apriori()
