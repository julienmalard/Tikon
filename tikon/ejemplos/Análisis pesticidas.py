from tikon0.Manejo.Aplicación import Insecticida
from tikon.rae.red_ae import RedAE


red_cocos = RedAE()
cocos = Cultivo('Coco')

insecticida = Insecticida('90%', proyecto=proyecto)
insecticida.estab_mortalidad(.90)

parc.aplicar(insecticida, día=[25, 50])
parc.simular()

parc.limpiar_aplicaciones()

específico = Insecticida('Específico', proyecto=proyecto)
específico.estab_mortalidad('Plagas', 0.90)

parc.aplicar(específico, día=[25, 50])
parc.simular()

parc.limpiar_especificados()
parc.aplicar_auto(insecticida, plaga='O. arenosella', densidad=20000)
parc.simular()

parc.limpiar_aplicaciones()
parc.aplicar_auto(específico, plaga='O. arenosella', densidad=20000)
parc.simular()
