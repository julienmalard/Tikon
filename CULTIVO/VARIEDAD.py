from NuevoCoso import Coso


# Esta clase representa una variedad de cultivo.
class Variedad(Coso):
    def __init__(símismo, nombre, directorio):
        # El diccionario de los datos para cada variedad de cultivo
        dic = dict(Nombre=nombre, Día_corto_crít=(), Pend_desarroll_fotoper=(), Tiempo_emerg_flor=(), Tiempo_flor_fruta=(),
                   Tiempo_flor_sem=(), Tiempo_sem_matur=(), Tiempo_flor_finhoja=(), Foto_máx=(),
                   Superfi_spec_hoja=(), Tamañ_hoja_máx=(), Máx_crec_semfrut=(), Peso_sem_máx=(),
                   Tiempo_llenar_sem=(), Sem_por_frut=(), Tiempo_llen_sem_opt=(), Ratio_sem_frut=(),
                   Frac_prot_sem=(), Frac_aceit_sem=(), Grupo_matur=(), Indic_adapt_temp=(), Taza_rep_min=(),
                   Tiempo_siembr_emer=(), Tiempo_emer_hoja=(), Tiempo_hoja_finjuv=(), Tiempo_inducflor=(),
                   Prop_tiemp_flor_frut=(), Prop_tiemp_sem_mat=(), Tiemp_frut=(), Tiemp_matfis_matcos=(),
                   Tiemp_flor_hoja=(), Taza_aparenc_hoja=(), Anch_rel_ecotipo=(), Altura_rel_ecotipo=(),
                   Aumen_sensit_día=(), Temp_min_flor=(), Pend_desarroll_flor=(), Tiempo_emerg_finjuv=(),
                   Atraso_desarroll_foto=(), Tiempo_rep_mat=(), Máx_semill_por_planta=(), Taza_opt_llen_sem=(),
                   Interval_emerg_hojas=(), Temp_base=(), Temp_opt=(), Temp_opt_rep=(),
                   Día_crit=(), Día_min_juv_rep=(), Días_emerg_porprofund=(), Días_rep_llen_sem=(),
                   Effic_uso_rad=(), Coef_extinct_luz=(), Temp_daño_hoja=(), Días_frios=(),
                   Superfi_máx_hoja=(), Long_hoja_máx=(), Part_C_rep=(), Part_C_rama_hoja=(),
                   Taza_expan_hoja=(), Taza_pot_crec_tub=(), Índice_supr_crec_tub=(), Sens_tub_fotoper=(),
                   Temp_crit_tub=(), Effic_uso_rad_stad1=(), Effic_uso_rad_otro_stad=(),
                   Tiempo_forzar_sepal=(), Tiempo_sepal_flor=(), Tiempo_flor_matur=(), Núm_ojos_poten=(),
                   Tasa_crec_ojos_poten=()
                   )
        super().__init__(nombre=nombre, ext='vrd', dic=dic, directorio=directorio)
