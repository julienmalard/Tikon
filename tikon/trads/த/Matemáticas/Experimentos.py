from tikon.Matemáticas.Experimentos import BD
from tikon.Matemáticas.Experimentos import BDsql
from tikon.Matemáticas.Experimentos import BDtexto
from tikon.Matemáticas.Experimentos import Experimento


class Experimento(Experimento):

    def obt_datos_rae(தன், egr, t_final=None, por_parcela=False):
        return super().obt_datos_rae(egr=egr, t_final=t_final, por_parcela=por_parcela)

    def obt_parcelas(தன், tipo):
        return super().obt_parcelas(tipo=tipo)

    def obt_info_parcelas(தன், parc):
        return super().obt_info_parcelas(parc=parc)

    def superficies(தன், parc):
        return super().superficies(parc=parc)

    def tiempo_final(தன், tipo):
        return super().tiempo_final(tipo=tipo)

    def agregar_pobs(தன், archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        return super().agregar_pobs(archivo=archivo, col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                    factor=factor, cód_na=cód_na)

    def agregar_muertes(தன், archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        return super().agregar_muertes(archivo=archivo, col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                       factor=factor, cód_na=cód_na)

    def agregar_reprs(தன், archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        return super().agregar_reprs(archivo=archivo, col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                     factor=factor, cód_na=cód_na)

    def agregar_trans_hacía(தன், archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        return super().agregar_trans_hacía(archivo=archivo, col_tiempo=col_tiempo, col_parc=col_parc,
                                           cols_etps=cols_etps, factor=factor, cód_na=cód_na)

    def agregar_crec(தன், archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        return super().agregar_crec(archivo=archivo, col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                    factor=factor, cód_na=cód_na)

    def agregar_parcelas(தன், archivo, col_nombres, col_superficies=None, col_polígonos=None, recalc_superf=False):
        return super().agregar_parcelas(archivo=archivo, col_nombres=col_nombres, col_superficies=col_superficies,
                                        col_polígonos=col_polígonos, recalc_superf=recalc_superf)

    def agregar_cultivos(தன், archivo):
        return super().agregar_cultivos(archivo=archivo)

    def agregar_aplicaciones(தன், archivo):
        return super().agregar_aplicaciones(archivo=archivo)

    def actualizar_fechas(தன், nueva_fecha_inic, días=None):
        return super().actualizar_fechas(nueva_fecha_inic=nueva_fecha_inic, días=días)

    def mover_fechas(தன், dif):
        return super().mover_fechas(dif=dif)

    def prep_archivo(தன், archivo):
        return super().prep_archivo(archivo=archivo)


class BD(BD):

    def sacar_cols(தன்):
        return super().sacar_cols()

    def obt_datos(தன், cols):
        return super().obt_datos(cols=cols)

    def obt_datos_tx(தன், cols):
        return super().obt_datos_tx(cols=cols)

    def obt_días(தன், col):
        return super().obt_días(col=col)

    def calc_n_obs(தன்):
        return super().calc_n_obs()

    def leer_fechas(lista_fechas):
        return super().leer_fechas()


class BDtexto(BDtexto):

    def calc_n_obs(தன்):
        return super().calc_n_obs()

    def obt_datos(தன், cols):
        return super().obt_datos(cols=cols)

    def obt_datos_tx(தன், cols):
        return super().obt_datos_tx(cols=cols)

    def sacar_cols(தன்):
        return super().sacar_cols()


class BDsql(BDsql):

    def calc_n_obs(தன்):
        return super().calc_n_obs()

    def obt_datos(தன், cols):
        return super().obt_datos(cols=cols)

    def obt_datos_tx(தன், cols):
        return super().obt_datos_tx(cols=cols)

    def sacar_cols(தன்):
        return super().sacar_cols()
