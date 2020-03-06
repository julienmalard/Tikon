from tikon.central import Exper, Parcela
from tikon.móds.rae.orgs.insectos import LotkaVolterra, Esfécido, Parasitoide, MetamCompleta, MetamIncompleta
from tikon.móds.rae.red import RedAE

sencillo = LotkaVolterra('sencillo')
otro_sencillo = LotkaVolterra('otro sencillo')
otro_más = LotkaVolterra('otro más')

esfécido = Esfécido('esfécido')
parasitoide = Parasitoide('parasitoide')
paras_con_pupa = Parasitoide('parasitoide con pupa', pupa=True)
hiperparasitoide = Parasitoide('hiperparasitoide')

metam_completa = MetamCompleta('metamórfosis completa')
metam_comp_sin_huevo = MetamCompleta('metamórfosis completa sin huevo', huevo=False)
metam_comp_sin_adulto = MetamCompleta('metamórfosis completa sin adulto', adulto=False)
metam_comp_2_juv = MetamCompleta('metamórfosis completa sin adulto', njuvenil=2)

metam_incompleta = MetamIncompleta('metamórfosis incompleta')
metam_incomp_sin_huevo = MetamCompleta('metamórfosis incompleta sin huevo', huevo=False)
metam_incomp_sin_adulto = MetamCompleta('metamórfosis incompleta sin adulto', adulto=False)
metam_incomp_2_juv = MetamCompleta('metamórfosis incompleta sin adulto', njuvenil=2)

red_1_insecto = RedAE([sencillo])

red_depred_mútliples = RedAE([sencillo, otro_sencillo, otro_más])
red_depred = RedAE([sencillo, otro_más])

with red_depred_mútliples:
    otro_más.secome(otro_sencillo)
    otro_sencillo.secome(sencillo)
    with red_depred:
        otro_más.secome(sencillo)

with RedAE([metam_completa, parasitoide]) as red_parasitismo:
    parasitoide.parasita(metam_completa)

with RedAE([esfécido, metam_completa]) as red_esfécido:
    esfécido.captura(metam_completa)

with RedAE([metam_completa, hiperparasitoide, paras_con_pupa]) as red_hiperparasitismo:
    paras_con_pupa.parasita(metam_completa)
    hiperparasitoide.parasita(paras_con_pupa)

with RedAE([parasitoide, metam_completa, metam_incompleta]) as red_paras_generalista:
    parasitoide.parasita(metam_completa)
    parasitoide.parasita(metam_incompleta)

exper = Exper('exper', Parcela('parc'))
