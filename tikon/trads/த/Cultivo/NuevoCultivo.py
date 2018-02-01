from tikon.Cultivo.NuevoCultivo import Cultivo
from tikon.Cultivo.NuevoCultivo import EnvolturaDSSAT
from tikon.Cultivo.NuevoCultivo import EnvolturaModCult
from tikon.Cultivo.NuevoCultivo import dic_info
from tikon.Cultivo.NuevoCultivo import mods_cult


class Cultivo(Cultivo):

    def estab_modelo(தன், programa, cód_modelo, dir_trabajo):
        return super().estab_modelo(programa=programa, cód_modelo=cód_modelo, dir_trabajo=dir_trabajo)

    def actualizar(தன்):
        return super().actualizar()

    def dibujar(தன், mostrar=True, directorio=None, exper=None):
        return super().dibujar(mostrar=mostrar, directorio=directorio, exper=exper)

    def especificar_apriori(தன்):
        return super().especificar_apriori()

    def incrementar(தன், paso, i, detalles, extrn):
        return super().incrementar(paso=paso, i=i, detalles=detalles, extrn=extrn)


class EnvolturaModCult(EnvolturaModCult):

    def prep_simul(தன், info_simul):
        return super().prep_simul(info_simul=info_simul)

    def empezar_simul(தன்):
        return super().empezar_simul()

    def incrementar(தன், paso, daño_plagas=None):
        return super().incrementar(paso=paso, daño_plagas=daño_plagas)

    def leer_resultados(தன்):
        return super().leer_resultados()


class EnvolturaDSSAT(EnvolturaDSSAT):

    def prep_simul(தன், info_simul):
        return super().prep_simul(info_simul=info_simul)

    def leer_resultados(தன்):
        return super().leer_resultados()


dic_info = dic_info

mods_cult = mods_cult
