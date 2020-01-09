from tikon.central import Exper, Parcela
from tikon.móds.rae.orgs.insectos import LotkaVolterra, Esfécido, Parasitoide, MetamCompleta, MetamIncompleta
from tikon.móds.rae.red import RedAE

sencillo = LotkaVolterra('sencillo')
otro_sencillo = LotkaVolterra('otro sencillo')
otro_más = LotkaVolterra('otro más')

esfécido = Esfécido('esfécido')
parasitoide = Parasitoide('parasitoide')
paras_con_pupa = Parasitoide('parasitoide con pupa', pupa=True)

metam_completa = MetamCompleta('metamórfosis completa')
metam_comp_sin_huevo = MetamCompleta('metamórfosis completa sin huevo', huevo=False)
metam_comp_sin_adulto = MetamCompleta('metamórfosis completa sin adulto', adulto=False)
metam_comp_2_juv = MetamCompleta('metamórfosis completa sin adulto', njuvenil=2)

metam_incompleta = MetamIncompleta('metamórfosis incompleta')
metam_incomp_sin_huevo = MetamCompleta('metamórfosis incompleta sin huevo', huevo=False)
metam_incomp_sin_adulto = MetamCompleta('metamórfosis incompleta sin adulto', adulto=False)
metam_incomp_2_juv = MetamCompleta('metamórfosis incompleta sin adulto', njuvenil=2)

red_1_insecto = RedAE([sencillo])

otro_sencillo.secome(sencillo)
otro_más.secome(sencillo)
otro_más.secome(otro_sencillo)
red_depred = RedAE([sencillo, otro_sencillo, otro_más])

red_depred_sub = RedAE([sencillo, otro_más])

parasitoide.parasita(metam_completa, etps_entra=['juvenil'], etp_emerg='pupa')
red_parasitismo = RedAE([metam_completa, parasitoide])

esfécido.captura(metam_completa, etps_presa='juvenil')
red_esfécido = RedAE([esfécido, metam_completa])

exper = Exper('exper', Parcela('parc'))
