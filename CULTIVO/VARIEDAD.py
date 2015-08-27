from COSO import Coso


# Esta clase representa una variedad de cultivo.
class Variedad(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada variedad de cultivo
        simismo.dic_base = dict(D�a_corto_cr�t=(), Pend_desarroll_fotoper=(), Tiempo_emerg_flor=(), Tiempo_flor_fruta=(),
                             Tiempo_flor_sem=(), Tiempo_sem_matur=(), Tiempo_flor_finhoja=(), Foto_m�x=(),
                             Superfi_spec_hoja=(), Tama�_hoja_m�x=(), M�x_crec_semfrut=(), Peso_sem_m�x=(),
                             Tiempo_llenar_sem=(), Sem_por_frut=(), Tiempo_llen_sem_opt=(), Ratio_sem_frut=(),
                             Frac_prot_sem=(), Frac_aceit_sem=(), Grupo_matur=(), Indic_adapt_temp=(), Taza_rep_min=(),
                             Tiempo_siembr_emer=(), Tiempo_emer_hoja=(), Tiempo_hoja_finjuv=(), Tiempo_inducflor=(),
                             Prop_tiemp_flor_frut=(), Prop_tiemp_sem_mat=(), Tiemp_frut=(), Tiemp_matfis_matcos=(),
                             Tiemp_flor_hoja=(), Taza_aparenc_hoja=(), Anch_rel_ecotipo=(), Altura_rel_ecotipo=(),
                             Aumen_sensit_d�a=(), Temp_min_flor=(), Pend_desarroll_flor=(), Tiempo_emerg_finjuv=(),
                             Atraso_desarroll_foto=(), Tiempo_rep_mat=(), M�x_semill_por_planta=(),
                             Taza_opt_llen_sem=(), Interval_emerg_hojas=(), Temp_base=(), Temp_opt=(), Temp_opt_rep=(),
                             D�a_crit=(), D�a_min_juv_rep=(), D�as_emerg_porprofund=(), D�as_rep_llen_sem=(),
                             Effic_uso_rad=(), Coef_extinct_luz=(), Temp_da�o_hoja=(), D�as_frios=(),
                             Superfi_m�x_hoja=(), Long_hoja_m�x=(), Part_C_rep=(), Part_C_rama_hoja=(),
                             Taza_expan_hoja=(), Taza_pot_crec_tub=(), �ndice_supr_crec_tub=(), Sens_tub_fotoper=(),
                             Temp_crit_tub=())
        super().__init__(*args, **kwargs)  # Esta variable se initializa como
        simismo.ext = "vrd"  # La extensi�n para este tipo de documento. (Para guadar y cargar datos.)
